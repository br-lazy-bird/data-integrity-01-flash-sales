import React from 'react';

const FlashSaleDescription: React.FC = () => {
  return (
    <div className="description">
      <div className="dialogue">
        <img src="/lazy-bird.png" alt="Lazy Bird" className="mascot-icon" />
        <p>
          "So, this is the flash sale system I mentioned in the <a href="https://github.com/br-lazy-bird/data-integrity-01-flash-sales/blob/main/README.md#the-problem" target="_blank" rel="noopener noreferrer">README</a>...
          We launched it today with only 1 book in stock. But customers are saying the system sold the same book twice. Stock went negative.
          The timestamps are like milliseconds apart. Something's definitely off, but I promised myself a coffee break 10 minutes ago, so...
          could you figure this out? Click Buy Now and see for yourself. Thanks!"
        </p>
      </div>
    </div>
  );
};

export default FlashSaleDescription;
