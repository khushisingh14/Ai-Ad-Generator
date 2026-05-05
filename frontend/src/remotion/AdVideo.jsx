import React from "react";
import { AbsoluteFill, Sequence, staticFile } from "remotion";

export const AdVideo = ({ scenes = [] }) => {
  const fps = 30;

  return (
    <AbsoluteFill style={{ backgroundColor: "#0f172a", color: "white", fontFamily: "Arial, sans-serif" }}>
      {scenes.map((scene) => (
        <Sequence key={scene.title} from={scene.start * fps} durationInFrames={(scene.end - scene.start) * fps}>
          <AbsoluteFill style={{ justifyContent: "center", padding: 80 }}>
            <div style={{ fontSize: 36, color: "#93c5fd", marginBottom: 24 }}>{scene.title}</div>
            <div style={{ fontSize: 68, lineHeight: 1.1, fontWeight: 700 }}>{scene.caption}</div>
            <div style={{ fontSize: 28, lineHeight: 1.4, marginTop: 36, color: "#cbd5e1" }}>{scene.visual}</div>
          </AbsoluteFill>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export default AdVideo;
