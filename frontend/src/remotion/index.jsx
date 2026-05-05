import { Composition } from "remotion";
import { AdVideo } from "./AdVideo";

export const RemotionRoot = () => (
  <Composition
    id="AdVideo"
    component={AdVideo}
    durationInFrames={1800}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={{ scenes: [] }}
  />
);
