import "../App.css";

function Explanation() {
  return (
    <div className="explanation">

      <h2>Understanding the System</h2>

      <p className="explain-intro">
        This simulator models how a serverless cloud system handles incoming requests
        using containers and machines. Below is a simple explanation of each parameter:
      </p>

      <div className="explain-grid">

        <div className="explain-card">
          <h3>Requests</h3>
          <p>
            Number of incoming user requests at a given time. 
            More requests mean more workload on the system.
          </p>
        </div>

        <div className="explain-card">
          <h3>Machines</h3>
          <p>
            Number of servers available. Each machine can run multiple containers,
            increasing the system’s total capacity.
          </p>
        </div>

        <div className="explain-card">
          <h3>Capacity</h3>
          <p>
            Maximum number of containers the system can support based on available machines.
            It represents the upper limit of the system.
          </p>
        </div>

        <div className="explain-card">
          <h3>Required</h3>
          <p>
            Number of containers needed to handle all incoming requests efficiently.
            This depends directly on the workload.
          </p>
        </div>

        <div className="explain-card">
          <h3>Prewarm</h3>
          <p>
            Containers prepared in advance before requests arrive. 
            Helps reduce delay by keeping resources ready.
          </p>
        </div>

        <div className="explain-card">
          <h3>Containers</h3>
          <p>
            Total containers actually allocated by the system to serve requests.
            This is the final decision made by the system.
          </p>
        </div>

        <div className="explain-card">
          <h3>Cold Start</h3>
          <p>
            Requests that had to wait because enough containers were not prewarmed.
            Lower cold start means better performance.
          </p>
        </div>

      </div>

      <p className="explain-summary">
        <b>Key Idea:</b> Required containers are handled using prewarmed containers and,
        if needed, additional cold-start containers. The goal is to minimize cold starts
        while efficiently using system resources.
      </p>

    </div>
  );
}

export default Explanation;