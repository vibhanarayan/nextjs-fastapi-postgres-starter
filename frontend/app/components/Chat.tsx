// components/Chat.tsx
'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Message {
  id?: number;
  content: string;
  user_id: number;
  timestamp?: string;
}

interface User {
  id: number;
  name: string;
}

const Chat: React.FC<{ user: User }> = ({ user }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [socket, setSocket] = useState<WebSocket | null>(null);



 useEffect(() => {
    const fetchMessages = async () => {
      try {
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/messages`);
        setMessages(response.data);
      } catch (error) {
        if (axios.isAxiosError(error)) {
          console.error('Error fetching messages:', error.message);
        } else {
          console.error('Unexpected error:', error);
        }
      }
    };

    fetchMessages();


    const newSocket = new WebSocket(`${process.env.NEXT_PUBLIC_API_URL!.replace('http', 'ws')}/ws`);
    setSocket(newSocket);

    newSocket.onmessage = (event) => {
      const message = event.data;
      setMessages((prevMessages) => [...prevMessages, { content: message, user_id: 0 }]);
    };

    return () => newSocket.close();
  }, []);


  const sendMessage = async () => {
    if (input.trim()) {
      const message = { content: input, user_id: user.id }; // Assuming user_id 1 for simplicity
      await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/messages`, message);
      setMessages((prevMessages) => [...prevMessages, message]);
      socket?.send(input);
      setInput('');
    }
  };

    const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <div className='flex flex-col items-center justify-center p-4 bg-gray-100 rounded-lg shadow-md'>
      <h1 className='text-2xl font-bold mb-4 text-black'>Chat with our bot </h1>
      <div className='w-full max-w-md bg-white rounded-lg shadow-md p-4 mb-4 overflow-y-auto max-h-96'>
          <div className='flex flex-col space-y-4'>
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${
                msg.user_id === 0 ? 'justify-start' : 'justify-end'
              }`}
            >
              <div
                className={`p-2 rounded-lg max-w-xs break-words ${
                  msg.user_id === 0
                    ? 'bg-blue-500 text-white self-start'
                    : 'bg-green-500 text-white self-end'
                }`}
              >
                {msg.content}
                 </div>
            </div>
          ))}
          </div>
      </div>
      <input
        type='text'
        value={input}
        onKeyDown={handleKeyDown}
        onChange={(e) => setInput(e.target.value)}
        className='w-full max-w-md p-2 border border-gray-300 text-black rounded-lg mb-2'
      />
      <button
        onClick={sendMessage}
        className='px-4 py-2 bg-blue-500 text-white rounded-lg'
      >
        Send
      </button>
    </div>
  );
};

export default Chat;
