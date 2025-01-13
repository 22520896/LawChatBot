import { useState, useEffect, useRef } from "react";
import { FaUser, FaRobot, FaPaperPlane, FaCircle, FaCommentDots } from "react-icons/fa";
import "./ChatBot.css";

const ChatBot = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const chatWindowRef = useRef(null);

  // Tự động cuộn xuống dưới cùng khi có tin nhắn mới
  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [messages]);

  // Xử lý gửi tin nhắn
  const handleSend = async () => {
    if (userInput.trim() === "" || isLoading) return; // Ngăn chặn gửi tin nhắn nếu đang tải

    // Thêm tin nhắn của người dùng và một dấu ba chấm của bot
    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: "user", text: userInput },
      { sender: "bot", text: "..." }, // Chỉ thêm một dấu ba chấm
    ]);

    setUserInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/process_query_stream/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userInput }),
      });

      if (!response.ok) {
        throw new Error("Lỗi khi gửi yêu cầu");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let botResponse = "";
      let isFirstChunk = true; // Biến để kiểm tra chunk đầu tiên

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Giải mã và cập nhật câu trả lời từng phần
        const chunk = decoder.decode(value);
        botResponse += chunk;

        // Nếu là chunk đầu tiên, thay thế dấu ba chấm bằng chunk đầu tiên
        if (isFirstChunk) {
          setMessages((prevMessages) => [
            ...prevMessages.filter((msg) => msg.text !== "..."), // Xóa dấu ba chấm
            { sender: "bot", text: botResponse }, // Thêm chunk đầu tiên
          ]);
          isFirstChunk = false; // Đánh dấu đã xử lý chunk đầu tiên
        } else {
          // Cập nhật tin nhắn cuối cùng của bot với chunk tiếp theo
          setMessages((prevMessages) => {
            const newMessages = [...prevMessages];
            const lastMessageIndex = newMessages.length - 1;
            if (newMessages[lastMessageIndex].sender === "bot") {
              newMessages[lastMessageIndex].text = botResponse;
            }
            return newMessages;
          });
        }
      }
    } catch (error) {
      console.error("Lỗi:", error);
      setMessages((prevMessages) => [
        ...prevMessages.filter((msg) => msg.text !== "..."), // Xóa dấu ba chấm
        { sender: "bot", text: "Đã xảy ra lỗi khi kết nối với chatbot." }, // Thêm thông báo lỗi
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Xử lý bắt đầu cuộc trò chuyện mới
  const handleNewChat = async () => {
    setMessages([]); // Reset messages về mảng rỗng
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
    }
  };

  // Định dạng câu trả lời của bot (in đậm các phần quan trọng)
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
        <FaRobot size={30} style={{ marginRight: "10px" }} /> {/* Thêm icon chatbot */}
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
            className={`message-container ${message.sender === "user" ? "user" : "bot"}`}
          >
            {message.sender === "user" && (
              <div className="icon-container user-icon">
                <FaUser />
              </div>
            )}
            <div
              className={`message ${message.sender} ${message.text === "..." ? "typing" : ""}`}
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
            onKeyPress={(e) => {
              if (e.key === "Enter" && !isLoading) {
                handleSend();
              }
            }}
          />
          <button
            onClick={handleSend}
            disabled={userInput.trim() === "" || isLoading} // Vô hiệu hóa nút gửi khi đang tải
            className={`send-button ${userInput.trim() === "" || isLoading ? "disabled" : ""}`}
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