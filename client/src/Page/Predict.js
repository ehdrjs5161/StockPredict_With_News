import React, {useState, useEffect} from 'react';
import Chart from '../Components/Chart';
import Info from "../Components/Info";
import Button from "@material-ui/core/Button";
import ButtonGroup from "@material-ui/core/ButtonGroup";

function Predict ({match}) {
    const [inititalData, setinitialData] = useState([{}])
    
    useEffect(() => {
        fetch(`/code/${match.params.code}`).then(
        response =>response.json([])
        ).then(data=>setinitialData(data))
    },[]);

    const data = inititalData;
    const predictDay1 = data['predict_day1'];
    
    return (
        <div>
            <Info code={data['code']} name = {data['name']} price={data['pre_close']} rate={data['pre_rate']} differ = {data['price_differ']}/>
            <ButtonGroup size="large" color="primary" aria-label="large outlined primary button group">
                <Button>전체 가격</Button>
                <Button>1일 예측</Button>
                <Button>7일 예측</Button>
            </ButtonGroup>
            <Chart data = {data['price_day1']}/>
            <b> 다음 개장일의 예측 종가: {predictDay1} KRW </b>
        </div>
    )
}

export default Predict;