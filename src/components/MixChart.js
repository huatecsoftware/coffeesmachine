import React from 'react'
import Highcharts from 'highcharts'
import Export from 'highcharts/modules/exporting'
import NoData from 'highcharts/modules/no-data-to-display'

Export(Highcharts)
NoData(Highcharts)

class MixChart extends React.Component {
    componentDidMount() {
        const { data } = this.props
        this.chart = this.initHighcharts(data)
    }
    componentDidUpdate() {
        this.chart.destroy()
        const { data } = this.props
        this.chart = this.initHighcharts(data)
    }
    shouldComponentUpdate(np, ns) {
        if (this.props.rangeStr.toString() !== np.rangeStr.toString()) {
            return true
        }
        if (this.props.data.length > 0) {
            if (np.data[2].len === this.props.data[2].len) {
                return false
            }
        }
        return true
    }
    initHighcharts = (data) => {
        Highcharts.setOptions({
            lang: {
                noData: '暂无数据',
            }
        })
        return Highcharts.chart('spline', {
            series: data,
            title: {
                text: '咖啡销量',
                style: {
                    fontSize: '2vw',
                    fontFamily: 'simsun',
                    fontWeight: 'bold'
                }
            },
            legend: {
                itemStyle: {
                    fontSize: '1vw',
                    fontFamily: 'simsun'
                }
            },
            tooltip: {
                useHTML: true,
                style: {
                    fontFamily: 'simsun',
                    fontSize: '1.5vw'
                },
                formatter: function () {
                    if (this.x === undefined) {
                        return `<span>总销量:${this.y}杯</span><br/><span>占比:${((this.y / this.total) * 100).toFixed(2)}%</span>`
                    } else {
                        return `<span>日期:${new Date(this.x).toLocaleDateString()}</span><br/><span>销量:${this.y}杯</span>`
                    }
                }
            },
            credits: { enabled: false },
            noData: {
                style: {
                    fontSize: '3vw',
                    fontFamily: 'simsun',
                    fontWeight: 'bold'
                }
            },
            chart: {
                zoomType: 'x',
                backgroundColor: 'transparent',
                options3d: {
                    enabled: true,
                }
            },
            yAxis: {
                gridLineWidth: 0.5,
                gridLineColor: 'gray',
                title: { text: null },
                labels: {
                    style: {
                        fontSize: '1vw',
                        color: 'black'
                    }
                },
            },
            plotOptions: {
                pie: {
                    dataLabels: {
                        style: {
                            fontSize: '1vw'
                        }
                    }
                },
                column: {
                    dataLabels: {
                        enabled: true,
                        style: {
                            fontSize: '1vw'
                        }
                    },
                    pointWidth: 40,
                    stacking: 'normal',
                }
            },
            xAxis: {
                type: 'datetime',
                min: new Date(this.props.rangeStr[0]).getTime(),
                max: new Date(this.props.rangeStr[1]).getTime(),
                gridLineWidth: 0.5,
                gridLineColor: 'gray',
                labels: {
                    style: {
                        fontSize: '1vw',
                        color: 'black'
                    }
                },
                dateTimeLabelFormats: {
                    year: '%Y',
                    day: '%m-%d',
                    week: '%m-%d',
                    hour: '%H:%M',
                    month: '%Y-%m',
                    minute: '%H:%M',
                    second: '%H:%M:%S',
                    millisecond: '%H:%M:%S.%L',
                },
            },
        })
    }

    render() {
        return <div id='spline' style={{ width: '100vw', height: '84vh' }}></div>
    }
}

export default MixChart