using System.Buffers;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;

namespace PlatynUI.JsonRpc;

/// <summary>
/// Handles framing, serialization and deserialization of JSON-RPC messages according to the LSP/DAP protocol format
/// (Content-Length header followed by JSON content).
/// </summary>
public class MessageFramer : IDisposable
{
    private readonly Stream _readerStream;
    private readonly Stream _writerStream;
    private readonly SemaphoreSlim _writeLock = new(1, 1);
    private readonly Encoding _encoding;
    private readonly string _contentType;
    private readonly JsonSerializerOptions _jsonOptions;
    private CancellationTokenSource? _ownCancellationSource;
    private bool _isDisposed;

    public MessageFramer(
        Stream readerStream,
        Stream writerStream,
        JsonSerializerOptions? jsonOptions = null,
        Encoding? encoding = null,
        string? contentType = null
    )
    {
        _readerStream = readerStream;
        _writerStream = writerStream;
        _encoding = encoding ?? Encoding.UTF8;
        _contentType = contentType ?? "application/vscode-jsonrpc";
        _jsonOptions = jsonOptions ?? new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase };
    }

    public MessageFramer(
        Stream stream,
        JsonSerializerOptions? jsonOptions = null,
        Encoding? encoding = null,
        string? contentType = null
    )
        : this(stream, stream, jsonOptions, encoding, contentType) { }

    /// <summary>
    /// Creates an enumerator that yields deserialized JsonElement objects from the stream.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token to stop enumeration.</param>
    /// <returns>An asynchronous enumerable of JsonElement objects.</returns>
    public async IAsyncEnumerable<JsonElement> ReadMessagesAsync(
        [EnumeratorCancellation] CancellationToken cancellationToken = default
    )
    {
        _ownCancellationSource?.Cancel();
        _ownCancellationSource = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        var combinedToken = _ownCancellationSource.Token;

        while (!combinedToken.IsCancellationRequested)
        {
            string? json = null;
            JsonElement element;

            try
            {
                json = await ReadRawMessageAsync(combinedToken);
                if (json == null)
                    yield break;

                element = JsonSerializer.Deserialize<JsonElement>(json, _jsonOptions);
            }
            catch (JsonException ex)
            {
                Console.Error.WriteLine($"Error parsing JSON: {ex.Message}. JSON: {json}");
                continue; // Skip to next message
            }
            catch (OperationCanceledException)
            {
                yield break;
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                Console.Error.WriteLine($"Error reading message: {ex.Message}");
                throw; // Rethrow non-cancellation exceptions
            }

            // Yield outside try/catch
            yield return element;
        }
    }

    /// <summary>
    /// Cancels any ongoing read operations.
    /// </summary>
    public void CancelReading()
    {
        _ownCancellationSource?.Cancel();
    }

    /// <summary>
    /// Deserializes and reads messages from the stream as specific types.
    /// </summary>
    /// <typeparam name="T">The type to deserialize each message to.</typeparam>
    /// <param name="cancellationToken">Cancellation token to stop enumeration.</param>
    /// <returns>An asynchronous enumerable of T objects.</returns>
    public async IAsyncEnumerable<T> ReadMessagesAsync<T>(
        [EnumeratorCancellation] CancellationToken cancellationToken = default
    )
        where T : class
    {
        await foreach (var element in ReadMessagesAsync(cancellationToken))
        {
            T? obj;

            try
            {
                obj = element.Deserialize<T>(_jsonOptions);
                if (obj == null)
                    continue;
            }
            catch (JsonException ex)
            {
                Console.Error.WriteLine($"Error deserializing to {typeof(T).Name}: {ex.Message}");
                continue; // Skip to next message
            }

            // Yield outside try/catch
            yield return obj;
        }
    }

    /// <summary>
    /// Sends a serialized message over the underlying stream.
    /// </summary>
    /// <param name="message">The object to serialize and send.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    public async Task SendMessageAsync(object message, CancellationToken cancellationToken = default)
    {
        string json;
        try
        {
            json = JsonSerializer.Serialize(message, _jsonOptions);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Error serializing message: {ex.Message}");
            throw;
        }

        await SendRawMessageAsync(json, cancellationToken);
    }

    /// <summary>
    /// Reads a raw message from the underlying stream.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token to cancel the read operation.</param>
    /// <returns>The content of the message as a string, or null if the stream was closed.</returns>
    public async Task<string?> ReadRawMessageAsync(CancellationToken cancellationToken = default)
    {
        var contentLength = 0;
        var hasContentLength = false;
        var encoding = _encoding;

        byte[] buffer = ArrayPool<byte>.Shared.Rent(4096);
        try
        {
            var headerBuilder = new StringBuilder(128);
            var inHeaderSection = true;
            var bufferPos = 0;
            var bufferLen = 0;

            while (inHeaderSection)
            {
                if (bufferPos >= bufferLen)
                {
                    bufferPos = 0;
                    bufferLen = await _readerStream.ReadAsync(buffer.AsMemory(0, buffer.Length), cancellationToken);

                    if (bufferLen == 0)
                        return null;
                }

                var availableData = buffer.AsSpan(bufferPos, bufferLen - bufferPos);
                var crlfIndex = -1;

                for (var i = 0; i < availableData.Length - 1; i++)
                {
                    if (availableData[i] == '\r' && availableData[i + 1] == '\n')
                    {
                        crlfIndex = i;
                        break;
                    }
                }

                if (crlfIndex >= 0)
                {
                    if (crlfIndex > 0)
                    {
                        var line = Encoding.ASCII.GetString(availableData[..crlfIndex]);
                        headerBuilder.Append(line);
                    }

                    var headerLine = headerBuilder.ToString();
                    headerBuilder.Clear();

                    var (headerName, headerValue) = SplitHeader(headerLine);

                    if (headerLine.Length == 0)
                    {
                        if (hasContentLength)
                            inHeaderSection = false;
                    }
                    else if (headerName.StartsWith("content-length", StringComparison.OrdinalIgnoreCase))
                    {
                        if (int.TryParse(headerValue, out var length) && length > 0)
                        {
                            hasContentLength = true;
                            contentLength = length;
                        }
                        else
                        {
                            LogError($"Invalid Content-Length value: {headerValue}");
                        }
                    }
                    else if (headerName.StartsWith("content-type", StringComparison.OrdinalIgnoreCase))
                    {
                        var contentType = headerValue;
                        var charsetToken = contentType
                            .Split(';')
                            .FirstOrDefault(s => s.Trim().StartsWith("charset=", StringComparison.OrdinalIgnoreCase));

                        if (charsetToken != null)
                        {
                            var charset = charsetToken.Split('=')[1].Trim();
                            try
                            {
                                encoding = Encoding.GetEncoding(charset);
                            }
                            catch (ArgumentException)
                            {
                                LogError($"Unsupported encoding: {charset}");
                                encoding = _encoding;
                            }
                        }
                    }

                    bufferPos += crlfIndex + 2;
                }
                else
                {
                    headerBuilder.Append(Encoding.ASCII.GetString(availableData));
                    bufferPos = bufferLen;
                }
            }

            if (contentLength <= 0)
                return null;

            var usePooledBuffer = contentLength > 8192;
            var contentBuffer = usePooledBuffer ? ArrayPool<byte>.Shared.Rent(contentLength) : new byte[contentLength];

            try
            {
                var bytesRead = 0;

                if (bufferPos < bufferLen)
                {
                    var bytesToCopy = Math.Min(bufferLen - bufferPos, contentLength);
                    Buffer.BlockCopy(buffer, bufferPos, contentBuffer, 0, bytesToCopy);
                    bytesRead = bytesToCopy;
                }

                while (bytesRead < contentLength)
                {
                    var read = await _readerStream.ReadAsync(
                        contentBuffer.AsMemory(bytesRead, contentLength - bytesRead),
                        cancellationToken
                    );

                    if (read == 0)
                        break;

                    bytesRead += read;
                }

                if (bytesRead == contentLength)
                {
                    return encoding.GetString(contentBuffer, 0, contentLength);
                }

                return null;
            }
            finally
            {
                if (usePooledBuffer && contentBuffer != null)
                {
                    ArrayPool<byte>.Shared.Return(contentBuffer);
                }
            }
        }
        finally
        {
            ArrayPool<byte>.Shared.Return(buffer);
        }
    }

    /// <summary>
    /// Sends a raw text message over the underlying stream.
    /// </summary>
    /// <param name="json">The JSON string to send.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>A task that completes when the message has been sent.</returns>
    public async Task SendRawMessageAsync(string json, CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(_isDisposed, this);

        if (string.IsNullOrEmpty(json))
        {
            LogError("Attempting to send empty message");
            return;
        }

        if (!await _writeLock.WaitAsync(TimeSpan.FromSeconds(30), cancellationToken).ConfigureAwait(false))
        {
            throw new TimeoutException("Timed out waiting for write lock");
        }

        try
        {
            var bodyBytes = _encoding.GetBytes(json);

            var headerBuilder = new StringBuilder();
            headerBuilder.Append("Content-Length: ").Append(bodyBytes.Length).Append("\r\n");

            if (_encoding != Encoding.UTF8)
            {
                headerBuilder
                    .Append($"Content-Type: {_contentType}; charset=")
                    .Append(_encoding.WebName)
                    .Append("\r\n");
            }

            headerBuilder.Append("\r\n");
            var header = headerBuilder.ToString();

            var headerBytes = Encoding.ASCII.GetBytes(header);
            var totalLen = headerBytes.Length + bodyBytes.Length;

            // Write header first
            await _writerStream.WriteAsync(headerBytes, cancellationToken);

            // Then write body
            await _writerStream.WriteAsync(bodyBytes, cancellationToken);
            await _writerStream.FlushAsync(cancellationToken);
        }
        catch (Exception ex)
        {
            LogError($"Error sending message: {ex.Message}");
            throw;
        }
        finally
        {
            _writeLock.Release();
        }
    }

    private static (string HeaderName, string HeaderValue) SplitHeader(string headerLine)
    {
        if (string.IsNullOrWhiteSpace(headerLine))
            return (string.Empty, string.Empty);

        var separatorIndex = headerLine.IndexOf(':');
        if (separatorIndex == -1)
            return (headerLine.Trim(), string.Empty);

        var headerName = headerLine[..separatorIndex].Trim();
        var headerValue = headerLine[(separatorIndex + 1)..].Trim();

        return (headerName, headerValue);
    }

    private static void LogError(string message)
    {
        Console.Error.WriteLine($"MessageFramer: {message}");
    }

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (_isDisposed)
            return;

        _isDisposed = true;

        if (disposing)
        {
            // Dispose managed resources
            _ownCancellationSource?.Cancel();
            _ownCancellationSource?.Dispose();
            _ownCancellationSource = null;
            _writeLock.Dispose();
        }

        // Free unmanaged resources (none in this case) and override a finalizer below.
    }

    ~MessageFramer()
    {
        Dispose(false);
    }
}
