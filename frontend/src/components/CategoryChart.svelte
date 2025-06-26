<script>
  import { onMount } from 'svelte';
  import {
    Chart,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    BarController
  } from 'chart.js';

  // Register Chart.js components
  Chart.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    BarController
  );

  export let data = {};

  let canvasEl;

  onMount(() => {
    if (data && Object.keys(data).length > 0) {
      new Chart(canvasEl, {
        type: 'bar',
        data: {
          labels: Object.keys(data),
          datasets: [{
            label: 'Addresses',
            data: Object.values(data),
            backgroundColor: 'rgba(59, 130, 246, 0.85)',
            borderColor: 'rgba(59, 130, 246, 1)',
            borderWidth: 2,
            borderRadius: 6,
            borderSkipped: false,
            barThickness: 10
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: 'rgba(30, 41, 59, 0.95)',
              titleColor: '#fff',
              bodyColor: '#fff',
              borderColor: 'rgba(255,255,255,0.2)',
              borderWidth: 1,
              cornerRadius: 8,
              displayColors: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: 'rgba(255,255,255,0.08)', drawBorder: false },
              ticks: {
                color: '#b0b8c1',
                font: { size: 9, weight: 'bold' },
                maxWidth: 100,
                callback: function(value) {
                  const label = this.getLabelForValue(value);
                  return label.length > 18 ? label.slice(0, 15) + '…' : label;
                }
              }
            },
            x: {
              grid: { display: false },
              ticks: { color: '#b0b8c1', font: { size: 11, weight: 'bold' } }
            }
          }
        }
      });
    }
  });
</script>

<div class="chart-container">
  <canvas bind:this={canvasEl}></canvas>
</div>

<style>
  .chart-container {
    height: 162px;
    width: 100%;
  }
</style> 