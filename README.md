# Chatroom Project with Django and Django Channels

This project implements a real-time chatroom using **Django**, **Django Channels**, and **WebSockets**. Below is a detailed overview of the project and solutions to the errors encountered during development.

---

## **Features**
- Real-time messaging using WebSockets.
- User authentication for access control.
- Message persistence using Django models.
- Display of past messages upon joining a room.

---

## **Setup Instructions**

### Prerequisites
- Python 3.8+
- Django 4.x
- Django Channels 4.x
- Redis (for the channel layer)

### Installation Steps
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd chatroom_project
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the Redis server (ensure Redis is installed):
   ```bash
   redis-server
   ```

5. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

7. In another terminal, run the Channels worker:
   ```bash
   daphne -b 127.0.0.1 -p 8001 chatProject.asgi:application
   ```

---

## **Project Structure**
```
chatProject/
├── chat/
│   ├── consumers.py      # WebSocket consumers
│   ├── models.py         # Message model
│   ├── urls.py           # App-specific routes
│   ├── views.py          # HTTP views (if any)
├── chatProject/
│   ├── asgi.py           # ASGI application for Channels
│   ├── settings.py       # Project settings
│   ├── urls.py           # Project-level routes
└── templates/
    └── chatroom.html     # Frontend for the chatroom
```

---

## **Major Issues Encountered and Solutions**

### **1. `apps aren’t loaded yet` Error**
**Description:** 
Encountered while importing models in `consumers.py`.

**Cause:**
The import statement for the `Message` model was placed at the top of the file. At the time of importing, Django’s app registry hadn’t been initialized.

**Solution:**
Move the import inside the function or method where the model is used.

```python
from chat.models import Message  # Moved this inside the `connect` method.
```

---

### **2. `SynchronousOnlyOperation` Error**
**Description:**
Raised when trying to access Django ORM from an asynchronous consumer.

**Cause:**
Django ORM operations are synchronous, and calling them directly from an async context (like `AsyncWebSocketConsumer`) is not allowed.

**Solution:**
Wrap the ORM operations with `sync_to_async`:

```python
from asgiref.sync import sync_to_async

past_messages = await sync_to_async(list)(
    Message.objects.filter(room_name=self.room_name).order_by('-timestamp')[:50]
)
```

---

### **3. WebSocket Connection Closing Automatically**
**Description:**
The WebSocket connection was closing when a user joined a room already occupied by another user.

**Cause:**
Errors in handling group communication (e.g., duplicate channel name registration) or unauthorized users accessing the chatroom.

**Solution:**
- Ensure user authentication is properly handled:

```python
if not self.scope['user'].is_authenticated:
    raise DenyConnection('You should be logged in to join this chatroom.')
```
- Add proper checks for group additions and removals:

```python
await self.channel_layer.group_add(
    self.room_group_name,
    self.channel_name
)
```

---

### **4. Incorrect Access to Related Fields**
**Description:**
Error when trying to access `message.sender.username` due to synchronous access in an async context.

**Solution:**
Fetch related fields asynchronously:

```python
await sync_to_async(Message.objects.create)(
    room_name=self.room_name,
    sender=self.scope['user'],
    message=message,
    timestamp=timezone.now()
)
```

---

### **5. `DenyConnection` Not Working Properly**
**Description:**
Unauthenticated users were still able to connect to the WebSocket.

**Cause:**
Improper handling of authentication check in the `connect` method.

**Solution:**
Raise `DenyConnection` explicitly if the user is not authenticated:

```python
if not self.scope['user'].is_authenticated:
    raise DenyConnection('You must be logged in to join this chatroom.')
```

---

## **How It Works**

### **Workflow of `ChatConsumer`**
1. **Connect:**
   - Authenticates the user.
   - Adds the user’s channel to a group corresponding to the chatroom.
   - Sends the past 50 messages to the user upon successful connection.

2. **Disconnect:**
   - Removes the user’s channel from the group.

3. **Receive Messages:**
   - Handles incoming messages from the WebSocket.
   - Saves the message to the database.
   - Broadcasts the message to other users in the room.

4. **Broadcast Messages:**
   - Ensures messages are sent to all users in the room except the sender.

---

## **Future Improvements**
- Add typing indicators.
- Support for media messages (images, videos).
- Add user presence (online/offline) indicators.
- Improve frontend with a modern JavaScript framework like React or Vue.

---

## **Acknowledgments**
This README was generated with the intent of documenting the entire development process, including the errors encountered and their solutions.
