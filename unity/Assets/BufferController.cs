using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BufferController : JunctionController
{
    private bool visible;
    private LineController connectingline;

    public void Setup(Vector2 position, LineController connectingline, bool autogenerated=false, bool visible=false) {
        gameObject.transform.position = position;
        GetComponent<MeshRenderer>().enabled = visible;

        this.position = position;
        this.connectingline = connectingline;
        this.visible = visible;
        this.autogenerated = autogenerated;
    }

    new public LineController nextLine(LineController fromline) {
        return null;
    }
}
