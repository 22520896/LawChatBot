import { useState, useEffect, useRef } from 'react'; // Thêm useRef và useEffect
import './ChatBot.css';

const ChatBot = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const chatWindowRef = useRef(null); // Tham chiếu đến cửa sổ chat

  // Tự động cuộn xuống tin nhắn mới nhất
  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [messages]); // Kích hoạt mỗi khi messages thay đổi

  const sendQueryToBackend = async (query) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/process_query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error('Lỗi khi gửi yêu cầu');
      }

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Lỗi:', error);
      return "Đã xảy ra lỗi khi kết nối với ChatBot.";
    }
  };

  const handleSend = async () => {
    if (userInput.trim() === "") return;

    // Thêm tin nhắn của người dùng vào danh sách tin nhắn
    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: "user", text: userInput },
    ]);

    // Xóa input của người dùng (sau khi đã nhận được phản hồi)
    setUserInput("");

    // Gửi yêu cầu đến backend và nhận phản hồi
    const botResponse = await sendQueryToBackend(userInput);

    // Thêm phản hồi từ chatbot vào danh sách tin nhắn
    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: "bot", text: botResponse },
    ]);

  };

  const handleNewChat = () => {
    setMessages([]); // Xóa tất cả tin nhắn
  };

  return (
    <div className="chatbot-container">
      <div className="chat-header">
        <h2>ChatBot</h2>
        <button className="new-chat-btn" onClick={handleNewChat}>
          New Chat
        </button>
      </div>

      {/* Thêm ref vào cửa sổ chat */}
      <div className="chat-window" ref={chatWindowRef}>
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            <p>{message.text}</p>
          </div>
        ))}
      </div>

      <div className="input-container">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Gõ câu hỏi của bạn..."
          onKeyPress={(e) => e.key === "Enter" && handleSend()}
        />
        <button onClick={handleSend}>Gửi</button>
      </div>
    </div>
  );
};

export default ChatBot;