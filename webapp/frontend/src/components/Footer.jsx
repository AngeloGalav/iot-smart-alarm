import './Footer.css'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
// Footer.js
import { FaBeer, FaGithub } from 'react-icons/fa';


const MyFooter = () => {
  return (
    <footer className="bg-neutral text-neutral-content text-center p-4">
      <div className="container mx-auto">
      <p>Made with ❤️ by Angelo Galavotti</p>
      </div>
      <div className='gh'><a href='https://github.com/AngeloGalav/iot-smart-alarm'><FaGithub /></a></div>
    </footer>
  );
};

export default MyFooter;
