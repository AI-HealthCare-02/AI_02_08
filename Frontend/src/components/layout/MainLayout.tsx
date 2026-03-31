import { Outlet } from "react-router-dom";

export default function MainLayout() {
  return (
    <div>
      <header>/* TODO: 네비게이션 바 */</header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
