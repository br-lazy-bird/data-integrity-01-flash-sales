import React from 'react';
import FlashSale from './components/FlashSale/FlashSale';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="container">
      <div className="app-wrapper">
        <h1 className="page-title">Lazy Bird</h1>
        <FlashSale />
      </div>
    </div>
  );
};

export default App;
