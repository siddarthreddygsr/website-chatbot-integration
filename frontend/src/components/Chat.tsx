'use client'

// import { useState } from 'react';
// import axios from 'axios';

// const Chat = () => {
//   const [messages, setMessages] = useState<{ text: string; type: 'sent' | 'received' }[]>([]);
//   const [inputText, setInputText] = useState<string>('');

//   const sendMessage = async () => {
//     if (inputText.trim() === '') return;

//     try {
//       // Add user message to chat as sent message immediately
//       const newSentMessage = { text: inputText, type: 'sent' };
//       setMessages(prevMessages => [...prevMessages, newSentMessage]); // Use functional update to ensure state is updated correctly
//       setInputText('');

//       // Send request to API endpoint
//       const response = await axios.post('http://localhost:8000/get_insights', {
//         target_text: inputText
//       });

//       // Update the chat with API response as received message

//       const receivedMessage = { text: response.data.response, type: 'received' };
//       setMessages(prevMessages => [...prevMessages, receivedMessage]); // Append received message to current messages
//     } catch (error) {
//       console.error('Error fetching response:', error);
//       // Handle error if needed
//     }
//   };

//   const handleKeyDown = async (e: React.KeyboardEvent<HTMLInputElement>) => {
//     if (e.key === 'Enter') {
//       e.preventDefault(); // Prevent default behavior (e.g., form submission)
//       sendMessage();
//     }
//   };

//   return (
//     <div className="flex flex-col min-h-screen relative min-w-lg">
//       <div className="flex-grow border rounded-lg max-w-lg min-w-lg mx-auto bg-white overflow-y-auto">
//         {messages.map((message, index) => (
//           <div
//             key={index}
//             className={`mb-2 ${message.type === 'sent' ? 'self-end bg-blue-500 text-white' : 'self-start bg-gray-300 text-gray-800'} p-2 rounded-lg`}
//             style={{ maxWidth: '70%', wordWrap: 'break-word' }}
//           >
//             <p>{message.text}</p>
//           </div>
//         ))}
//       </div>
//       <div className="fixed bottom-0 left-0 right-0 bg-white p-4 border-t border-gray-300 flex items-center justify-center max-w-lg mx-auto">
//         <input
//           type="text"
//           value={inputText}
//           onChange={(e) => setInputText(e.target.value)}
//           onKeyDown={handleKeyDown} // Handle Enter key down
//           placeholder="Type your message..."
//           className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
//           style={{ marginRight: '10px' }}
//         />
//         <button
//           onClick={sendMessage}
//           className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
//         >
//           Send
//         </button>
//       </div>
//     </div>
//   );
// };

// export default Chat;

'use client'

import { useState } from 'react';
import axios from 'axios';

type ChatMessage = {
  text: string;
  type: 'sent' | 'received';
  sources?: string[]; // Optional field for sources
};

const Chat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState<string>('');

  const sendMessage = async () => {
    if (inputText.trim() === '') return;

    try {
      // Add user message to chat as sent message immediately
      const newSentMessage: ChatMessage = { text: inputText, type: 'sent' };
      setMessages(prevMessages => [...prevMessages, newSentMessage]); // Use functional update to ensure state is updated correctly
      setInputText('');

      // Send request to API endpoint
      const response = await axios.post('http://localhost:8000/get_insights', {
        target_text: inputText
      });

      // Extract response text and sources
      const responseText = response.data.response;
      const sources = response.data.sources;

      // Update the chat with API response as received message
      const receivedMessage: ChatMessage = { text: responseText, type: 'received' };
      const sourceMessage: ChatMessage = { text: 'Sources:', type: 'received', sources: sources };

      setMessages(prevMessages => [...prevMessages, receivedMessage, sourceMessage]); // Append received message and sources to current messages
    } catch (error) {
      console.error('Error fetching response:', error);
      // Handle error if needed
    }
  };

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault(); // Prevent default behavior (e.g., form submission)
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col min-h-screen relative">
      <div className="flex-grow rounded-lg max-w-lg mx-auto bg-white overflow-y-auto py-15 my-15" style={{ paddingBottom: "100px", width: "32rem"}}>
        {messages.map((message, index) => (
          <div
            key={index}
            className={`mb-2 ${message.type === 'sent' ? 'self-end bg-blue-500 text-white ml-auto text-right' : 'self-start bg-gray-300 text-gray-800'} p-2 w-[fit-content] rounded-lg`}
            style={{ maxWidth: '70%', wordWrap: 'break-word' }}
          >
            <p>{message.text}</p>
            {message.sources && (
              <div className="mt-2">
                {message.sources.map((source, i) => (
                  <a key={i} href={source} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">
                    {source}
                  </a>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="fixed bottom-0 left-0 right-0 bg-white p-4 border-t border-gray-300 flex items-center justify-center max-w-lg mx-auto">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyDown} // Handle Enter key down
          placeholder="Type your message..."
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          style={{ marginRight: '10px' }}
        />
        <button
          onClick={sendMessage}
          className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default Chat;
