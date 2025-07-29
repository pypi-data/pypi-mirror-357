using System.Buffers;
using System.Collections.Concurrent;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.VisualStudio.Threading;

namespace PlatynUI.JsonRpc;

public enum JsonRpcErrorCode
{
    ParseError = -32700,
    InvalidRequest = -32600,
    MethodNotFound = -32601,
    InvalidParams = -32602,
    InternalError = -32603,
}

// Add JSON-RPC version constant
public static class JsonRpcConstants
{
    public const string JSON_RPC_VERSION = "2.0";
}

public abstract record JsonRpcMessage
{
    [JsonPropertyName("jsonrpc")]
    public string JsonRpc { get; init; } = JsonRpcConstants.JSON_RPC_VERSION;
}

public record JsonRpcRequest : JsonRpcMessage
{
    [JsonPropertyName("method")]
    public required string Method { get; init; }

    [JsonPropertyName("params")]
    public JsonElement? Params { get; set; } = null;

    [JsonPropertyName("id")]
    public required JsonElement? Id { get; set; }
}

public record JsonRpcNotification : JsonRpcMessage
{
    [JsonPropertyName("method")]
    public required string Method { get; init; }

    [JsonPropertyName("params")]
    public JsonElement? Params { get; set; } = null;
}

public abstract record JsonResponseBase : JsonRpcMessage { }

public record JsonRpcResponse : JsonResponseBase
{
    [JsonPropertyName("result")]
    [JsonIgnore(Condition = JsonIgnoreCondition.Never)]
    public object? Result { get; set; }

    [JsonPropertyName("id")]
    public required JsonElement Id { get; set; }
}

public class JsonRpcError
{
    [JsonPropertyName("code")]
    public int Code { get; set; }

    [JsonPropertyName("message")]
    public required string Message { get; set; }

    [JsonPropertyName("data")]
    public object? Data { get; set; }
}

public record JsonRpcErrorResponse : JsonResponseBase
{
    [JsonPropertyName("error")]
    public required JsonRpcError Error { get; set; }

    [JsonPropertyName("id")]
    [JsonIgnore(Condition = JsonIgnoreCondition.Never)]
    public required JsonElement? Id { get; set; }
}

public class JsonRpcPeer : IDisposable
{
    public JsonRpcPeer(Stream readerStream, Stream writerStream)
    {
        ReaderStream = readerStream;
        WriterStream = writerStream;

        JsonSerializerOptions = new()
        {
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        };

        _messageFramer = new MessageFramer(
            readerStream,
            writerStream,
            JsonSerializerOptions,
            defaultEncoding,
            defaultContentType
        );
    }

    public JsonRpcPeer(Stream stream)
        : this(stream, stream) { }

    public readonly Stream ReaderStream;
    public readonly Stream WriterStream;
    private readonly MessageFramer _messageFramer;
    private bool _isDisposed;

    public JoinableTaskFactory? JoinableTaskFactory { get; set; }

    private readonly ConcurrentDictionary<
        string,
        Func<JsonElement?, JsonSerializerOptions, Task<object?>>
    > requestHandlers = new();
    private readonly ConcurrentDictionary<
        string,
        Func<JsonElement?, JsonSerializerOptions, Task>
    > notificationHandlers = new();

    private readonly ConcurrentDictionary<string, TaskCompletionSource<JsonRpcResponse>> pendingRequests = new();
    private int idCounter = 1;
    private readonly Encoding defaultEncoding = Encoding.UTF8;
    private readonly string defaultContentType = "application/vscode-jsonrpc";

    private Task? messageLoopTask;
    private CancellationTokenSource? cancellationTokenSource;

    public JsonSerializerOptions JsonSerializerOptions { get; }

    private readonly TaskCompletionSource<bool> completionSource = new();

    public Task<bool> Completion => completionSource.Task;

    public void Start()
    {
        ThrowIfDisposed();

        if (messageLoopTask == null)
        {
            cancellationTokenSource = new CancellationTokenSource();
            messageLoopTask = Task.Run(() => MessageLoopAsync(cancellationTokenSource.Token));
        }
    }

    public void Stop()
    {
        if (cancellationTokenSource != null)
        {
            cancellationTokenSource.Cancel();
            _messageFramer.CancelReading();
            cancellationTokenSource = null;
            messageLoopTask = null;
        }
    }

    private void ThrowIfDisposed()
    {
        if (_isDisposed)
            throw new ObjectDisposedException(nameof(JsonRpcPeer));
    }

    public void RegisterRequestHandler<T>(string methodName, Func<JsonElement?, JsonSerializerOptions, Task<T>> handler)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(methodName);

        if (requestHandlers.ContainsKey(methodName))
        {
            throw new ArgumentException(
                $"Request handler for method '{methodName}' already exists",
                nameof(methodName)
            );
        }
        requestHandlers[methodName] = async (parameters, options) => await handler(parameters, options);
    }

    public void RegisterNotificationHandler(string methodName, Func<JsonElement?, JsonSerializerOptions, Task> handler)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(methodName);
        if (notificationHandlers.ContainsKey(methodName))
        {
            throw new ArgumentException(
                $"Notification handler for method '{methodName}' already exists",
                nameof(methodName)
            );
        }
        notificationHandlers[methodName] = handler;
    }

    protected static void LogError(string message)
    {
        Console.Error.WriteLine(message);
    }

    public void SendNotification(string method, object? @params)
    {
        if (JoinableTaskFactory != null)
        {
            JoinableTaskFactory.Run(async () => await SendNotificationAsync(method, @params));
        }
        else
        {
            Task.Run(async () => await SendNotificationAsync(method, @params)).GetAwaiter().GetResult();
        }
    }

    public async Task SendNotificationAsync(string method, object? @params)
    {
        ThrowIfDisposed();

        var message = new JsonRpcNotification
        {
            Method = method,
            Params = @params != null ? JsonSerializer.SerializeToElement(@params, JsonSerializerOptions) : null,
        };
        await _messageFramer.SendMessageAsync(message);
    }

    public void SendRequest(string method)
    {
        SendRequest<object>(method, null);
    }

    public void SendRequest(string method, object? @params)
    {
        SendRequest<object>(method, @params);
    }

    public T SendRequest<T>(string method)
    {
        return SendRequest<T>(method, null);
    }

    public T SendRequest<T>(string method, object? @params)
    {
        if (JoinableTaskFactory != null)
        {
            return JoinableTaskFactory.Run(async () => await SendRequestAsync<T>(method, @params));
        }
        else
        {
            return Task.Run(async () => await SendRequestAsync<T>(method, @params)).GetAwaiter().GetResult();
        }
    }

    public async Task SendRequestAsync(string method)
    {
        await SendRequestAsync<object>(method, null);
    }

    public async Task SendRequestAsync(string method, object? @params)
    {
        await SendRequestAsync<object>(method, @params);
    }

    public async Task<T> SendRequestAsync<T>(string method)
    {
        return await SendRequestAsync<T>(method, null);
    }

    public async Task<T> SendRequestAsync<T>(string method, object? @params)
    {
        ThrowIfDisposed();

        var id = Interlocked.Increment(ref idCounter).ToString();
        var message = new JsonRpcRequest
        {
            Method = method,
            Params = @params != null ? JsonSerializer.SerializeToElement(@params, JsonSerializerOptions) : null,
            Id = JsonSerializer.SerializeToElement(id),
        };

        var tcs = new TaskCompletionSource<JsonRpcResponse>(TaskCreationOptions.RunContinuationsAsynchronously);
        pendingRequests[id] = tcs;

        await _messageFramer.SendMessageAsync(message);

        // Add a timeout to prevent hanging indefinitely
        using var timeoutCts = new CancellationTokenSource(TimeSpan.FromMinutes(5));
        using var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(
            timeoutCts.Token,
            cancellationTokenSource?.Token ?? CancellationToken.None
        );

        try
        {
            var responseTask = tcs.Task;
            var completedTask = await Task.WhenAny(responseTask, Task.Delay(-1, linkedCts.Token));

            if (completedTask != responseTask)
            {
                if (timeoutCts.IsCancellationRequested)
                    throw new TimeoutException($"Request {method} timed out after 30 seconds");

                throw new OperationCanceledException("The request was cancelled");
            }

            var response = await responseTask;

            if (response.Result is JsonElement jsonElement)
            {
                T? result = jsonElement.Deserialize<T>(JsonSerializerOptions);

                if (result == null && !IsNullable(typeof(T)))
                {
                    throw new InvalidOperationException(
                        $"Deserialization resulted in null for non-nullable type {typeof(T).FullName}"
                    );
                }

                return result!;
            }

            return (T)default!;
        }
        finally
        {
            // Clean up the pending request if needed
            pendingRequests.TryRemove(id, out _);
        }
    }

    private static bool IsNullable(Type type)
    {
        return Nullable.GetUnderlyingType(type) != null || !type.IsValueType;
    }

    protected async Task MessageLoopAsync(CancellationToken cancellationToken)
    {
        try
        {
            await foreach (var jsonElement in _messageFramer.ReadMessagesAsync(cancellationToken))
            {
                try
                {
                    await ProcessJsonElementAsync(jsonElement);
                }
                catch (Exception ex)
                {
                    LogError($"Error processing message: {ex.Message}");
                    try
                    {
                        await _messageFramer.SendMessageAsync(
                            new JsonRpcErrorResponse
                            {
                                Error = new JsonRpcError
                                {
                                    Code = (int)JsonRpcErrorCode.InternalError,
                                    Message = ex.Message,
                                    Data = ex.StackTrace,
                                },
                                Id = null,
                            }
                        );
                    }
                    catch (Exception sendEx)
                    {
                        LogError($"Failed to send error response: {sendEx.Message}");
                    }
                }
            }
        }
        catch (OperationCanceledException)
        {
            // Normal cancellation, just exit
            completionSource.TrySetResult(false);
            return;
        }
        catch (Exception e)
        {
            LogError($"Message loop terminated with error: {e.Message}");
            completionSource.TrySetException(e);
            return;
        }

        completionSource.TrySetResult(true);
    }

    private async Task ProcessJsonElementAsync(JsonElement jsonElement)
    {
        if (jsonElement.ValueKind == JsonValueKind.Array)
        {
            var responses = new List<object>();

            foreach (var element in jsonElement.EnumerateArray())
            {
                var response = await ProcessSingleMessage(element);
                if (response != null)
                {
                    responses.Add(response);
                }
            }

            if (responses.Count > 0)
            {
                await _messageFramer.SendMessageAsync(responses);
            }
        }
        else
        {
            var response = await ProcessSingleMessage(jsonElement);
            if (response != null)
            {
                await _messageFramer.SendMessageAsync(response);
            }
        }
    }

    protected async Task<JsonResponseBase?> ProcessSingleMessage(JsonElement jsonElement)
    {
        // If it's a response (has id and no method), we should be more tolerant of version differences
        bool isResponse = jsonElement.TryGetProperty("id", out var _) && !jsonElement.TryGetProperty("method", out _);

        if (jsonElement.TryGetProperty("jsonrpc", out var versionProperty))
        {
            // Only enforce version check for requests/notifications, not for responses
            if (versionProperty.GetString() != JsonRpcConstants.JSON_RPC_VERSION && !isResponse)
            {
                return new JsonRpcErrorResponse
                {
                    Id = null,
                    Error = new JsonRpcError
                    {
                        Code = (int)JsonRpcErrorCode.InvalidRequest,
                        Message = $"Unsupported JSON-RPC version: {versionProperty.GetString()}",
                    },
                };
            }
        }
        else if (!isResponse) // Only require jsonrpc property for requests/notifications
        {
            // If jsonrpc property is missing entirely
            return new JsonRpcErrorResponse
            {
                Id = null,
                Error = new JsonRpcError
                {
                    Code = (int)JsonRpcErrorCode.InvalidRequest,
                    Message = "Missing required 'jsonrpc' property",
                },
            };
        }

        if (jsonElement.TryGetProperty("id", out var idProperty) && !jsonElement.TryGetProperty("method", out _))
        {
            if (
                idProperty.ValueKind != JsonValueKind.Null
                && pendingRequests.TryRemove(idProperty.ToString(), out var tcs)
            )
            {
                if (jsonElement.TryGetProperty("error", out var errorProperty))
                {
                    var error = errorProperty.Deserialize<JsonRpcError>(JsonSerializerOptions);
                    tcs.SetException(new Exception($"RPC Error {error?.Code}: {error?.Message} ({error?.Data})"));
                }
                else if (jsonElement.TryGetProperty("result", out var resultProperty))
                {
                    var response = new JsonRpcResponse { Id = idProperty, Result = resultProperty };
                    tcs.SetResult(response);
                }
                else
                {
                    tcs.SetException(new Exception("RPC Error: Invalid response format"));
                }
                return null;
            }
            else if (
                idProperty.ValueKind == JsonValueKind.Null
                && jsonElement.TryGetProperty("error", out var errorProperty)
            )
            {
                var error = errorProperty.Deserialize<JsonRpcError>(JsonSerializerOptions);
                LogError($"Received error with null ID: {error?.Code}: {error?.Message} ({error?.Data})");

                return null;
            }
        }
        else if (jsonElement.TryGetProperty("method", out var methodProperty))
        {
            if (
                jsonElement.TryGetProperty("id", out var requestIdProperty)
                && requestIdProperty.ValueKind != JsonValueKind.Null
            )
            {
                var message =
                    jsonElement.Deserialize<JsonRpcRequest>(JsonSerializerOptions)
                    ?? throw new JsonException("Invalid request format");
                return await ProcessRequestAsync(message, requestIdProperty);
            }
            else
            {
                var message =
                    jsonElement.Deserialize<JsonRpcNotification>(JsonSerializerOptions)
                    ?? throw new JsonException("Invalid notification format");
                return await ProcessNotificationAsync(message);
            }
        }

        return null;
    }

    protected async Task<JsonResponseBase> ProcessRequestAsync(JsonRpcRequest message, JsonElement requestId)
    {
        if (requestHandlers.TryGetValue(message.Method, out var handler))
        {
            try
            {
                var result = await handler(message.Params, JsonSerializerOptions);
                return new JsonRpcResponse { Id = requestId, Result = result };
            }
            catch (Exception ex)
            {
                return new JsonRpcErrorResponse
                {
                    Id = requestId,
                    Error = new JsonRpcError
                    {
                        Code = (int)JsonRpcErrorCode.InternalError,
                        Message = ex.Message,
                        Data = ex.StackTrace,
                    },
                };
            }
        }
        else
        {
            return new JsonRpcErrorResponse
            {
                Id = requestId,
                Error = new JsonRpcError
                {
                    Code = (int)JsonRpcErrorCode.MethodNotFound,
                    Message = $"Method for request {message?.Method} not found",
                },
            };
        }
    }

    protected async Task<JsonResponseBase?> ProcessNotificationAsync(JsonRpcNotification message)
    {
        if (notificationHandlers.TryGetValue(message.Method, out var handler))
        {
            try
            {
                await handler(message.Params, JsonSerializerOptions);
                return null;
            }
            catch (Exception ex)
            {
                return new JsonRpcErrorResponse
                {
                    Id = null,
                    Error = new JsonRpcError
                    {
                        Code = (int)JsonRpcErrorCode.InternalError,
                        Message = ex.Message,
                        Data = ex.StackTrace,
                    },
                };
            }
        }
        else
        {
            return new JsonRpcErrorResponse
            {
                Id = null,
                Error = new JsonRpcError
                {
                    Code = (int)JsonRpcErrorCode.MethodNotFound,
                    Message = $"Method for notification {message?.Method} not found",
                },
            };
        }
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
            try
            {
                Stop();

                // Cancel all pending requests
                foreach (var (_, tcs) in pendingRequests)
                {
                    tcs.TrySetCanceled();
                }
                pendingRequests.Clear();

                // Dispose the message framer
                _messageFramer.Dispose();

                // Set completion if not already done
                completionSource.TrySetResult(false);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Error during JsonRpcPeer disposal: {ex.Message}");
            }
        }

        // Free unmanaged resources (none in this case)
    }

    ~JsonRpcPeer()
    {
        Dispose(false);
    }
}
