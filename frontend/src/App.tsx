import { ChatWidget } from "./components/ChatWidget";

function App() {
  return (
    <main className="demoPage">
      <section className="demoContent">
        <h1>Vidco Dijital Yardım Asistanı — Demo</h1>
        <p>
          Sağ alttaki chat balonuna tıklayarak Vidco Dijital Yardım Asistanı
          widgetını test edebilirsiniz.
        </p>
      </section>

      <ChatWidget />
    </main>
  );
}

export default App;