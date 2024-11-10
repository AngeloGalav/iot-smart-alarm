import './Footer.css'
import { FaGithub } from 'react-icons/fa';

const MyFooter = () => {
    return (
        <>
            <footer className='mt-1 footer' style={{ backgroundColor: "black", height: "15vh" }}>
                <div className='text-white p-3'>
                    Made with ❤️ by Angelo Galavotti
                </div>
                <a href="https://github.com/AngeloGalav/iot-smart-alarm" className='text-white p-2' style={{ fontSize: "30px" }}>
                    <FaGithub />
                </a>
            </footer>
        </>
    );
};

export default MyFooter;