import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";

function DatasetView({ simulated = [] }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/dataset")
      .then(res => res.json())
      .then(d => setData(d.data || []));
  }, []);

  return (
    <div>
      <h2  style={{"font-size":"30px"}}>Dataset vs Simulation</h2>

      <Line
        data={{
          labels: data.map((_, i) => i),
          datasets: [
            {
              label: "Actual Data",
              data,
              borderColor: "#3b82f6",
              borderWidth: 2,
              pointRadius: 0
            },
            {
              label: "Simulated Containers",
              data: simulated,
              borderColor: "#22c55e",
              borderWidth: 2,
              pointRadius: 0
            }
          ]
        }}
      />
    </div>
  );
}

export default DatasetView;