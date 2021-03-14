import React from 'react';
import {LineChart, Line, YAxis, XAxis, CartesianGrid, Tooltip, Legend} from 'recharts';
function Chart (props) {
    return (
        <div>
            <LineChart width={1200}
                height={500}
                data = {props.data}
            >
                <CartesianGrid strokeDasharray=""/>
                <YAxis yAxisId="right" orientation="right"/>
                <YAxis dataKey="Price"/>
                <XAxis dataKey="Date"/>
                <Tooltip/>
                <Legend/>
                <Line type="monotone" dataKey="Price" stroke="#8884d8" activeDot="r:8"/>
            </LineChart>
        </div>
    )
}

export default Chart;