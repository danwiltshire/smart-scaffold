from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType
from copilot.session import PermissionHandler
from halo import Halo


async def apply_recipe(prompt: str, system_message: str, token: str):
    async with CopilotClient() as client:
        session = await client.create_session(
            on_permission_request=PermissionHandler.approve_all,
            model="gpt-5.4",
            system_message={"mode": "append", "content": system_message},
            reasoning_effort="low",
            reasoning_summary="concise",
            streaming=True,
            mcp_servers={
                "github": {
                    "type": "http",
                    "url": "https://api.githubcopilot.com/mcp/",
                    "headers": {"Authorization": f"Bearer {token}"},
                    "tools": [
                        "get_file_contents",  # list directory contents and read .md files
                        "create_branch",  # create a uniquely named branch before writing
                        "create_or_update_file",  # write SOP and CONTEXT.md files to the branch
                        "create_pull_request",  # open a PR for review once files are written
                    ],
                }
            },
        )

        spinner = Halo(text="Applying recipe...", spinner="dots")
        spinner.start()

        final_message = ""
        error_message: str | None = None

        def handler(event):
            nonlocal final_message, error_message

            if event.type == SessionEventType.ASSISTANT_REASONING:
                if event.data.content:
                    spinner.text = event.data.content
            elif event.type == SessionEventType.ASSISTANT_MESSAGE:
                if event.data.content:
                    final_message = event.data.content
                    spinner.text = event.data.content
            elif event.type == SessionEventType.SESSION_ERROR:
                error_message = event.data.message

        session.on(handler)

        try:
            await session.send_and_wait(prompt, timeout=300.0)
        except Exception as exc:
            spinner.fail(error_message or str(exc))
            raise

        if error_message:
            spinner.fail(error_message)
        else:
            spinner.succeed(final_message or "Done")
