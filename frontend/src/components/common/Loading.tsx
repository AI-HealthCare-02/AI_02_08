// 재사용 가능한 로딩 컴포넌트
export interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export const Loading: React.FC<LoadingProps> = ({ 
  size = 'md', 
  text = '로딩 중...' 
}) => {
  return (
    <div className="loading-container">
      <div className={`loading-spinner loading-${size}`}></div>
      {text && <p className="loading-text">{text}</p>}
    </div>
  );
};