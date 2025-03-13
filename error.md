when attempting to call an async tool function with shiny/agno, this error is thrown.
```
Traceback (most recent call last):
  File "/Users/jeffbryner/development/illuminAIte/.venv/lib/python3.12/site-packages/shiny/reactive/_extended_task.py", line 131, in _execution_wrapper
    return await self._func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jeffbryner/development/illuminAIte/.venv/lib/python3.12/site-packages/shiny/ui/_chat.py", line 689, in _stream_task
    return await self._append_message_stream(message, icon=icon)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jeffbryner/development/illuminAIte/.venv/lib/python3.12/site-packages/shiny/ui/_chat.py", line 746, in _append_message_stream
    async for msg in message:
  File "/Users/jeffbryner/development/illuminAIte/.venv/lib/python3.12/site-packages/shiny/_utils.py", line 508, in __anext__
    value = next(self.iterator)
            ^^^^^^^^^^^^^^^^^^^
  File "/Users/jeffbryner/development/illuminAIte/lib/utils.py", line 44, in as_stream
    for chunk in response:
                 ^^^^^^^^
  File "/Users/jeffbryner/development/illuminAIte/.venv/lib/python3.12/site-packages/agno/agent/agent.py", line 536, in _run
    for model_response_chunk in self.model.response_stream(messages=run_messages.messages):
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jeffbryner/development/illuminAIte/.venv/lib/python3.12/site-packages/agno/models/base.py", line 506, in response_stream
    for function_call_response in self.run_function_calls(
                                  ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jeffbryner/development/illuminAIte/.venv/lib/python3.12/site-packages/agno/models/base.py", line 843, in run_function_calls
    function_call_result = self._create_function_call_result(
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jeffbryner/development/illuminAIte/.venv/lib/python3.12/site-packages/agno/models/base.py", line 774, in _create_function_call_result
    return Message(
           ^^^^^^^^
  File "/Users/jeffbryner/development/illuminAIte/.venv/lib/python3.12/site-packages/pydantic/main.py", line 214, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 2 validation errors for Message
content.list[any]
  Input should be a valid list [type=list_type, input_value=<coroutine object PlotlyC...ic_chart at 0x1301d92a0>, input_type=coroutine]
    For further information visit https://errors.pydantic.dev/2.10/v/list_type
content.str
  Input should be a valid string [type=string_type, input_value=<coroutine object PlotlyC...ic_chart at 0x1301d92a0>, input_type=coroutine]
    For further information visit https://errors.pydantic.dev/2.10/v/string_type

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/jeffbryner/development/illuminAIte/.venv/lib/python3.12/site-packages/shiny/reactive/_reactives.py", line 584, in _run
    await self._fn()
  File "/Users/jeffbryner/development/illuminAIte/.venv/lib/python3.12/site-packages/shiny/ui/_chat.py", line 701, in _handle_error
    await self._raise_exception(e)
  File "/Users/jeffbryner/development/illuminAIte/.venv/lib/python3.12/site-packages/shiny/ui/_chat.py", line 355, in _raise_exception
    raise NotifyException(msg, sanitize=sanitize) from e
shiny.types.NotifyException: Error in Chat('chat_session-chat'): 2 validation errors for Message
content.list[any]
  Input should be a valid list [type=list_type, input_value=<coroutine object PlotlyC...ic_chart at 0x1301d92a0>, input_type=coroutine]
    For further information visit https://errors.pydantic.dev/2.10/v/list_type
content.str
  Input should be a valid string [type=string_type, input_value=<coroutine object PlotlyC...ic_chart at 0x1301d92a0>, input_type=coroutine]
    For further information visit https://errors.pydantic.dev/2.10/v/string_type
```

despite attempts to return a string, none, etc the error persists.