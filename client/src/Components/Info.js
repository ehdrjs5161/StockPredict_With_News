import React from 'react';

function Info(props){
     return(
        <div>
            <h1>{props.code} {props.name}</h1> 
            <b>{props.price} KRW {props.differ > 0? <b style={{color: 'red'}}>+{props.differ}</b> : <b style={{color: "blue"}}>{props.differ}</b>}
            {props.rate > 0 ? <b style={{color: 'red'}}>(▲{props.rate}%)</b> : <b style={{color: 'blue'}}>(▼{props.rate}%)</b>}</b>
            <p></p>
        </div>
    )
}
export default Info;