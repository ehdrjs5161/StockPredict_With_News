import React from "react";
import { render } from "react-dom";
import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts/highstock";
import MyStockChart from './MyStockChart.js';

class Chart extends React.PureComponent {
  constructor(props) {
    super(props);
    this.afterChartCreated = this.afterChartCreated.bind(this);
    const price = this.props.data;
    const date = this.props.date;
    this.state = {
      chartOptions: {
        series: [
          {
            data: price
          }
        ],
        xAxis: {
          labels: {
            useHTML: true,
            formatter: function () {
              return Highcharts.dateFormat("%y.%m.%d", this.date);
            }
          }
        }
      }
    };
  }

  afterChartCreated(chart) {
    this.internalChart = chart;
    this.forceUpdate();
  }

  componentDidUpdate() {
    //this.internalChart.getMargins(); // redraw
    this.internalChart.reflow();
  }

  render() {
    const chart = this.internalChart;

    return (
      <div>
        <HighchartsReact
          highcharts={Highcharts}
          constructorType={"stockChart"}
          options={this.state.chartOptions}
          callback={this.afterChartCreated}
        />
      </div>
    );
  }
}

// const Chart = () => <div>
//   <MyStockChart />
// </div>

export default Chart;
 