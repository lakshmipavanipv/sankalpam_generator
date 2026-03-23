export default function LoadingSpinner() {
  return (
    <div className="spinner-container" role="status" aria-label="Loading">
      <div className="lotus-spinner">
        <div className="petal p1">🪷</div>
        <div className="petal p2">🪷</div>
        <div className="petal p3">🪷</div>
        <div className="petal p4">🪷</div>
        <div className="spinner-center">ॐ</div>
      </div>
    </div>
  );
}
