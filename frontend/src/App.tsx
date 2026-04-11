import React from 'react'
import './App.css'
import AppRouter from './routes/AppRouter'
import { ToastProvider } from './contexts/ToastContext'
import ToastContainer from './components/common/ToastContainer'

const App: React.FC = () => {
  return (
    <ToastProvider>
      <div className="App">
        <AppRouter />
        <ToastContainer />
      </div>
    </ToastProvider>
  )
}

export default App
