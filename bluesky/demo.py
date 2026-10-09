from .simulation import run_simulation
from .visualizer import render_html


def main() -> None:
    snapshots, events = run_simulation()
    output = render_html(snapshots, events, "bluesky/outputs/demo.html")

    print("AGORA Blue Sky demo")
    print("=" * 40)
    for snap in snapshots:
        print(f"Round {snap['round']}: {snap['label']}")
        for agent in snap["agents"].values():
            print(
                f"  {agent.id}: position={agent.position:+.2f}, "
                f"strength={agent.strength:.2f}, evidence={len(agent.evidence)}"
            )
    print(f"\nVisualization written to: {output}")


if __name__ == "__main__":
    main()
