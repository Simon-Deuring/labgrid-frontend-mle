import { Component, OnInit } from '@angular/core';
import Chart from 'chart.js/auto';

@Component({
  selector: 'app-chart',
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.css']
})
export class ChartComponent implements OnInit {

  title = 'dashboard';
  chartLine: any;
  chartRadar: any;

  constructor() { }

  ngOnInit(): void {
    this.chartLine = this.getLineChart();
    this.chartRadar = this.getRadarChart();
  }

  getLineChart() {
    return new Chart('canvasLine',
      {
        type: 'line',
        data: {
          labels: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'],
          datasets: [
            {
              label: 'My First dataset',
              data: [1, 3, 5, 10, 56, 65, 35, 543, 543, 543],
              backgroundColor:  'rgba(255,89,94, 0.1)',
              borderColor: 'rgba(255,89,94, 1)',
              fill: false
            },
            {
              label: 'My Second dataset',
              data: [26, 20, 5, 10, 56, 123, 35, 360, 412, 478],
              backgroundColor: 'rgba(63, 81, 181, 0.1)',
              borderColor: 'rgba(63, 81, 181, 1)',
              fill: false,
              tension: 0.1
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Chart.js Line Chart'
            }
          }
        },
      });  
  }
  getRadarChart() {
    return new Chart('canvasRadar',
      {
        type: 'radar',
        data: {
          labels: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
          datasets: [
            {
              label: 'My First dataset',
              data: [1, 80, 56, 150, 56, 65, 345, 543],
              backgroundColor: 'rgba(255,89,94, 0.1)',
              borderColor: 'rgba(255,89,94, 1)',
              fill: true
            },
            {
              label: 'My Second dataset',
              data: [80, 3, 234, 245, 200, 150, 87, 150],
              backgroundColor: 'rgba(63, 81, 181, 0.1)',
              borderColor: 'rgba(63, 81, 181, 1)',
              fill: true
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Chart.js Radar Chart'
            }
          }
        },
      });
  
  }
}
