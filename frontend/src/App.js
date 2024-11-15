import './App.css';
import Hero from './components/Hero';
import MyFooter from './components/Footer';


function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <Hero />
      <MyFooter />
    </div>
  );
}

export default App;
