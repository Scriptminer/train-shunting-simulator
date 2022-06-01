// https://answers.unity.com/questions/614288/pan-camera-with-mouse.html

using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class CameraHandler : MonoBehaviour {
    [SerializeField] public float mouseSensitivity = 0.075f;
    private Vector3 lastPosition;

    void Update(){
        if (Input.GetMouseButtonDown(0)){
            lastPosition = Input.mousePosition;
            // Modified from: https://www.c-sharpcorner.com/article/how-to-detect-mouse-click-or-touch-on-a-gameobject-using-c-sharp-script-in-unity3d/
            Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
            RaycastHit hit;
            if (Physics.Raycast(ray, out hit)) {
                if (hit.transform.name == "TriPoints(Clone)") {
                    hit.transform.GetComponent<TriPointsController>().SwitchLine();
                }
            }
            // End of copied section
        }

        if (Input.GetMouseButton(0)){
            Vector3 delta = lastPosition - Input.mousePosition;
            transform.Translate(delta.x * mouseSensitivity, delta.y * mouseSensitivity, 0);
            lastPosition = Input.mousePosition;
        }
    }
}
