type FeedbackButtonsProps = {
  value?: "up" | "down";
  onRate: (rating: "up" | "down") => void;
};

export function FeedbackButtons({ value, onRate }: FeedbackButtonsProps) {
  if (value) {
    return <div className="feedbackButtons feedbackDone">Geri bildiriminiz için teşekkürler.</div>;
  }

  return (
    <div className="feedbackButtons">
      <button
        className="feedbackButton"
        onClick={() => onRate("up")}
        aria-label="Bu cevap faydalı oldu"
        type="button"
      >
        👍
      </button>

      <button
        className="feedbackButton"
        onClick={() => onRate("down")}
        aria-label="Bu cevap faydalı olmadı"
        type="button"
      >
        👎
      </button>
    </div>
  );
}