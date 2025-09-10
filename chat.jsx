import axios from "axios";
import { useState } from "react";

function ChatPage() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");

  const askBackend = async () => {
    const res = await axios.post("http://localhost:5000/ask", {
      query,
      role: "HR"
    });
    setAnswer(res.data.answer + " (Source: " + res.data.citation + ")");
  };

  return (
    <div>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <button onClick={askBackend}>Ask</button>
      <p>{answer}</p>
    </div>
  );
}

export default ChatPage;
