import { ChatWidget } from "./components/ChatWidget";

function App() {
  return (
    <main className="demoPage">
      <section className="demoContent">
        <h1>Vidco 17020 RAG Assistant Demo</h1>
        <p>
          Sağ alttaki chat balonuna tıklayarak Vidco Yardım Asistanı widgetını
          test edebilirsiniz.
        </p>
      </section>

      <ChatWidget />
    </main>
  );
}

export default App;