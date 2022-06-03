using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Carriage : MonoBehaviour
{
    [SerializeField] GameObject carriageNodePrefab;
    LineController lineOccupied;
    public float fractionalPosition;
    public float length;
    public string type;

    public CarriageNode front;
    public CarriageNode back;

    public void Setup(LineController lineOccupied, float fractionalPosition, float length, string type="default"){
        this.length = length;
        this.fractionalPosition = fractionalPosition;

        this.front = Instantiate(carriageNodePrefab, new Vector3(0,0,0), Quaternion.identity).GetComponent<CarriageNode>();
        this.back  = Instantiate(carriageNodePrefab, new Vector3(0,0,0), Quaternion.identity).GetComponent<CarriageNode>();
        this.front.Setup(lineOccupied, fractionalPosition);
        this.back.Setup(lineOccupied, fractionalPosition);
    }

    public CarriageNode GetLeader(float velocity){
        if (velocity > 0){
            return front;
        } else{
            return back;
        }
    }

    public CarriageNode GetFollower(float velocity){
        if (velocity > 0){
            return back;
        } else{
            return front;
        }
    }

    void Update()
    {
        Vector2 pos = (front.GetPosition() + back.GetPosition()) / 2.0f;
        gameObject.transform.position = new Vector3(pos.x,pos.y,1);
    }

}
