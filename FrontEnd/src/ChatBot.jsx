import { useState, useEffect, useRef } from "react";
import { FaUser, FaRobot, FaPaperPlane, FaCircle, FaCommentDots } from "react-icons/fa";
import "./ChatBot.css";

const ChatBot = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const chatWindowRef = useRef(null);

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [messages]);

  const sendQueryToBackend = async (query) => {
    try {
      const response = await fetch("http://127.0.0.1:8000/process_query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error("Lỗi khi gửi yêu cầu");
      }

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error("Lỗi:", error);
      return "Đã xảy ra lỗi khi kết nối với chatbot.";
    }
  };

  const handleSend = async () => {
    if (userInput.trim() === "") return;

    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: "user", text: userInput },
    ]);

    setUserInput("");
    setIsLoading(true);

    const botResponse = await sendQueryToBackend(userInput);

    setMessages((prevMessages) => [
      ...prevMessages.filter((msg) => msg.text !== "..."),
      { sender: "bot", text: botResponse },
    ]);

    setIsLoading(false);
  };

  const handleNewChat = async () => {
    // setIsLoading(true);
    // Reset messages về mảng rỗng
    setMessages([]);
    try {
      const response = await fetch("http://127.0.0.1:8000/newchat/", {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error("Lỗi khi khởi tạo lại chatbot");
      }

      const data = await response.json();
      console.log(data.message); // Chỉ log ra console, không thêm vào tin nhắn

    } catch (error) {
      console.error("Lỗi:", error);
      // Nếu có lỗi, hiển thị thông báo lỗi trong console, không thêm vào tin nhắn
    }
    // finally {
    //   setIsLoading(false);
    // }
  };

  useEffect(() => {
    if (isLoading) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "bot", text: "..." },
      ]);
    }
  }, [isLoading]);

  const formatBotResponse = (text) => {
    return text.split("\n").map((line, index) => (
      <p key={index}>
        {line.split("**").map((part, i) => {
          if (i % 2 === 1) {
            return (
              <span key={i} style={{ fontWeight: "bold" }}>
                {part}
              </span>
            );
          }
          return <span key={i}>{part}</span>;
        })}
      </p>
    ));
  };

  return (
    <div className="chatbot-container">
      <div className="chat-header">
        <h1>CHATBOT HỎI ĐÁP VỀ LUẬT HÔN NHÂN VÀ GIA ĐÌNH VIỆT NAM</h1>
        <button className="new-chat-btn" onClick={handleNewChat} title="Bắt đầu cuộc trò chuyện mới">
          <FaCommentDots size={24} color="white" />
        </button>
      </div>

      <div className="chat-window" ref={chatWindowRef}>
        {messages.length === 0 && (
          <div className="welcome-container">
            <div className="welcome-message">
              <h1>
                <FaRobot size={30} style={{ marginRight: "10px" }} />
                XIN CHÀO!
              </h1>
              Bạn có câu hỏi nào cần tôi hỗ trợ không?
            </div>
          </div>
        )}
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message-container ${message.sender === "user" ? "user" : "bot"
              }`}
          >
            {message.sender === "user" && (
              <div className="icon-container user-icon">
                <FaUser />
              </div>
            )}
            <div
              className={`message ${message.sender} ${message.text === "..." ? "typing" : ""
                }`}
            >
              {message.sender === "bot" && message.text === "..." ? (
                <div className="typing-indicator">
                  <FaCircle className="dot dot1" />
                  <FaCircle className="dot dot2" />
                  <FaCircle className="dot dot3" />
                </div>
              ) : message.sender === "bot" ? (
                formatBotResponse(message.text)
              ) : (
                <p>{message.text}</p>
              )}
            </div>
            {message.sender === "bot" && (
              <div className="icon-container bot-icon">
                <FaRobot />
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="input-container">
        <div className="input-wrapper">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Nhập câu hỏi..."
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
          />
          <button
            onClick={handleSend}
            disabled={userInput.trim() === ""}
            className={`send-button ${userInput.trim() === "" ? "disabled" : ""}`}
            title="Gửi"
          >
            <FaPaperPlane size={20} color="white" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatBot;