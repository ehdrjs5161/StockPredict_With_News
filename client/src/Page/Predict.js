import React, {useState, useEffect} from 'react';
import Chart from '../Components/Chart';
import Info from "../Components/Info";
import Button from "@material-ui/core/Button";
import ButtonGroup from "@material-ui/core/ButtonGroup";

export default function Predict ({match}) {
    const [data, setData] = useState([{}])
    useEffect(() => {
        fetch(`/code/${match.params.code}`).then(
        response =>response.json([])
        ).then(data=>setData(data))
    },[]);
    console.log(data)
    const price = data['price']
    const date = data['date']
    console.log(data.price_day1)
    // const predictDay1 = data['Price'];
    // console.log(data['price_day1'])
    const temp = [1,2,3,4,9,2,0,1]
    return (
        <div>
            <Info code={data['code']} name = {data['name']} price={data['pre_close']} rate={data['pre_rate']} differ = {data['price_differ']}/>
            {/* <ButtonGroup size="large" color="primary" aria-label="large outlined primary button group">
                <Button>전체 가격</Button>
                <Button>1일 예측</Button>
                <Button>7일 예측</Button>
            </ButtonGroup> */}
            <Chart data = {temp} date={date}/>
            {/* <b> 다음 개장일의 예측 종가: {predictDay1} KRW </b> */}
        </div>
    )
}