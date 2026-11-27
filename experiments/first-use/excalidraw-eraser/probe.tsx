import React from "react";
import { expect, it } from "vitest";
import { Excalidraw } from "../index";
import { fireEvent, mockBoundingClientRect, render, restoreOriginalGetBoundingClientRect } from "./test-utils";

it("observes two freehand taps after one eraser drag", async () => {
  mockBoundingClientRect({ width: 800, height: 600 });
  try {
    const view = await render(<Excalidraw />);
    const { app, state } = window.h;
    const canvas = view.container.querySelector("canvas.interactive")!;
    const scene = app.scene;
    const pointer = (clientX: number, clientY: number, pressed: boolean) => ({
      clientX, clientY, pointerId: 1, pointerType: "mouse", button: 0,
      buttons: pressed ? 1 : 0, pressure: pressed ? 0.5 : 0, altKey: false,
    });
    expect([state.zoom.value, state.scrollX, state.scrollY, state.offsetLeft, state.offsetTop])
      .toEqual([1, 0, 0, 0, 0]);
    fireEvent.click(view.getByToolName("freedraw"));
    for (const [x, y] of [[100, 100], [180, 160]]) {
      fireEvent.pointerDown(canvas, pointer(x, y, true));
      fireEvent.pointerUp(canvas, pointer(x, y, false));
    }

    const dots = scene.getNonDeletedElements();
    expect(dots).toHaveLength(2);
    for (const [index, dot] of dots.entries()) {
      expect(dot).toMatchObject({
        type: "freedraw", x: [100, 180][index], y: [100, 160][index],
        points: [[0, 0], [0.0001, 0.0001]], strokeWidth: 2, angle: 0,
        simulatePressure: true, locked: false, isDeleted: false,
      });
    }
    fireEvent.click(view.getByToolName("eraser"));
    expect(window.h.state.activeTool.type).toBe("eraser");
    expect(app.visibleElements.map(el => el.id)).toEqual(dots.map(el => el.id));
    fireEvent.pointerDown(canvas, pointer(80, 101, true));
    fireEvent.pointerMove(canvas, pointer(120, 101, true));
    fireEvent.pointerUp(canvas, pointer(120, 101, false));

    const all = scene.getElementsIncludingDeleted();
    expect(all.map(el => el.id)).toEqual(dots.map(el => el.id));
    const live = scene.getNonDeletedElements();
    const result = dots.map(dot => {
      const el = all.find(item => item.id === dot.id)!;
      const present = live.some(item => item.id === dot.id);
      expect(present).toBe(!el.isDeleted);
      return { x: el.x, y: el.y, isDeleted: el.isDeleted, present };
    });
    expect(result[1].present).toBe(true);
    console.log("ERASER_SCENE " + JSON.stringify(result));
  } finally {
    restoreOriginalGetBoundingClientRect();
  }
});
