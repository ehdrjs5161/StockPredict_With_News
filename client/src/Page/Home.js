import React, {useState} from 'react';
import {Route} from 'react-router-dom';
import Search from "../Components/Search";
const Home = () => {
    // const [input, setInput] = useState('');
    // const onChange = (e) => {
    //     setInput(e.target.value);
    // };

    // const goPage = (e) => {
    //     <Route path="/code/:value" componet={e.target.value}/>
    // };

    return (
        <div className="App">
            <Search/>
        </div>
    );
};

export default Home;