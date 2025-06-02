-- Create the chat_conversation table
CREATE TABLE IF NOT EXISTS chat_conversation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- Create the chat_conversation_participants table for the many-to-many relationship
CREATE TABLE IF NOT EXISTS chat_conversation_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES chat_conversation (id),
    FOREIGN KEY (user_id) REFERENCES auth_user (id),
    UNIQUE (conversation_id, user_id)
);

-- Create the chat_message table
CREATE TABLE IF NOT EXISTS chat_message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    is_read BOOLEAN NOT NULL,
    conversation_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES chat_conversation (id),
    FOREIGN KEY (sender_id) REFERENCES auth_user (id)
);
