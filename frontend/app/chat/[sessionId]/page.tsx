
export default async function ChatPage({params}: {params: Promise<{sessionId: string}>}) {
  const sessionId = (await params).sessionId

  const response = await fetch(`http://127.0.0.1:8000/chat/session/${sessionId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    }})
  
  const instructions = await response.json()
  console.log("response: ", instructions)


  return (
    <div className="chat-container">
      {instructions.response}
      
    </div>
  )
}
