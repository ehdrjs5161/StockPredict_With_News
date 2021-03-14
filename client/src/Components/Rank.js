import { React, useEffect, useState, Component } from 'react';
function Rank() {
  const [data, setData] = useState([{}]);
  
  useEffect(() => {
    fetch('/rank').then(
      response => response.json([])
    ).then(data=>setData(data))
  },[{}]);
  const rank = data['068270'];
  console.log(rank);
  return(
    <div>
      <h1>아이 싯팔!</h1>
    </div>
  );
 }

export default Rank;