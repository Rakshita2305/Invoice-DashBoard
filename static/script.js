document.addEventListener("DOMContentLoaded", function () {
    const chartCanvas = document.getElementById("chart");
  
    if (chartCanvas) {
      const chartLabels = JSON.parse(chartCanvas.dataset.labels);
      const chartValues = JSON.parse(chartCanvas.dataset.values);
  
      const ctx = chartCanvas.getContext("2d");
      new Chart(ctx, {
        type: "bar",
        data: {
          labels: chartLabels,
          datasets: [
            {
              label: "Outstanding Amount",
              data: chartValues,
              backgroundColor: "rgba(13, 110, 253, 0.7)",
            },
          ],
        },
      });
    }
  });
  