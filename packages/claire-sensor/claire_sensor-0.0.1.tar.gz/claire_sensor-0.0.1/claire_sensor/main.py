from enum import Enum

from fastapi import FastAPI

app = FastAPI()

class MessagingOperation(str, Enum):
    send = "send"
    receive = "receive"
    check = "check"

@app.get("/")
async def root():
    return {"message": "Hello World from Claire-sensor agent"}

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}

@app.get("/operations/{operation}")
async def get_model(operation: MessagingOperation, address: str, msg_count: int = 0):
    if operation is MessagingOperation.send:
        log_msg = f"Sending {msg_count} messages to {address}"
        return {"operation": operation, "message": log_msg, "address": address, "count": msg_count}

    if operation.value == MessagingOperation.receive:
        log_msg = f"Receiving {msg_count} messages from {address}"
        return {"operation": operation, "message": log_msg, "address": address, "count": msg_count}

    log_msg = f"Checking address {address} for expected message count"
    return {"operation": operation, "message": log_msg, "address": address, "expected_count": msg_count}

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    # create file /tmp/xxx & return content of it
    # use in URL "//" to get leading "/" in path
    content = ""
    with open("/tmp/xxx", "w") as file:
        file.write("Hello, this is some text written to a file!\n")
        file.write("Another line here.\n")

    with open(file_path, "r") as file:
        content = file.read()
    return {"file_path": file_path, "content": content}



# Optional CLI launcher
def run():
    import uvicorn
    uvicorn.run("claire_sensor.main:app", host="0.0.0.0", port=8123)