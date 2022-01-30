using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using System.Threading;

public class CSharpForGIT : MonoBehaviour
{
    Thread mThread;
    public string connectionIP = "127.0.0.1";
    public int connectionPort = 25001;
    IPAddress localAdd;
    TcpListener listener;
    TcpClient client;
    float[] receivedData = new float[23];

    bool running;

    private void Update()
    {
        GameObject thumb1 = GameObject.Find("b_r_thumb1");
        GameObject thumb2 = GameObject.Find("b_r_thumb2");
        GameObject thumb3 = GameObject.Find("b_r_thumb3");
        thumb3.transform.localRotation = Quaternion.Euler(new Vector3(0,0,-receivedData[0]));
        thumb2.transform.localRotation = Quaternion.Euler(new Vector3(0,receivedData[10],-receivedData[5]+20));
        thumb1.transform.localRotation = Quaternion.Euler(new Vector3(receivedData[16]-7,receivedData[10]-10,receivedData[15]));
        GameObject index1 = GameObject.Find("b_r_index1");
        GameObject index2 = GameObject.Find("b_r_index2");
        GameObject index3 = GameObject.Find("b_r_index3");
        index3.transform.localRotation = Quaternion.Euler(new Vector3(0,0,-receivedData[19]));
        index2.transform.localRotation = Quaternion.Euler(new Vector3(0,0,-receivedData[1]));
        index1.transform.localRotation = Quaternion.Euler(new Vector3(0,receivedData[11]+5,-receivedData[6]));
        GameObject middle1 = GameObject.Find("b_r_middle1");
        GameObject middle2 = GameObject.Find("b_r_middle2");
        GameObject middle3 = GameObject.Find("b_r_middle3");
        middle3.transform.localRotation = Quaternion.Euler(new Vector3(0,0,-receivedData[20]));
        middle2.transform.localRotation = Quaternion.Euler(new Vector3(0,0,-receivedData[2]));
        middle1.transform.localRotation = Quaternion.Euler(new Vector3(0,receivedData[12],-receivedData[7]));
        GameObject ring1 = GameObject.Find("b_r_ring1");
        GameObject ring2 = GameObject.Find("b_r_ring2");
        GameObject ring3 = GameObject.Find("b_r_ring3");
        ring3.transform.localRotation =  Quaternion.Euler(new Vector3(0,0,-receivedData[21]));
        ring2.transform.localRotation =  Quaternion.Euler(new Vector3(0,0,-receivedData[3]));
        ring1.transform.localRotation =  Quaternion.Euler(new Vector3(0,receivedData[13]-3,-receivedData[8]));
        GameObject pinky0 = GameObject.Find("b_r_pinky0");
        GameObject pinky1 = GameObject.Find("b_r_pinky1");
        GameObject pinky2 = GameObject.Find("b_r_pinky2");
        GameObject pinky3 = GameObject.Find("b_r_pinky3");
        pinky3.transform.localRotation = Quaternion.Euler(new Vector3(0,0,-receivedData[22]));
        pinky2.transform.localRotation = Quaternion.Euler(new Vector3(0,0,-receivedData[4]));
        pinky1.transform.localRotation = Quaternion.Euler(new Vector3(0,receivedData[14]-10,-receivedData[9]));
        pinky0.transform.localRotation = Quaternion.Euler(new Vector3(-5,10,0));
        GameObject wrist = GameObject.Find("b_r_wrist");
        wrist.transform.localRotation = Quaternion.Euler(new Vector3(0,-receivedData[17],-receivedData[18]));
    }

    private void Start()
    {
        ThreadStart ts = new ThreadStart(GetInfo);
        mThread = new Thread(ts);
        mThread.Start();
    }

    void GetInfo()
    {
        localAdd = IPAddress.Parse(connectionIP);
        listener = new TcpListener(IPAddress.Any, connectionPort);
        listener.Start();

        client = listener.AcceptTcpClient();

        while (true)
        {
            SendAndReceiveData();
        }
        listener.Stop();
    }

    void SendAndReceiveData()
    {
        NetworkStream nwStream = client.GetStream();
        byte[] buffer = new byte[client.ReceiveBufferSize];
        print("hello");

        //---receiving Data from the Host----
        int bytesRead = nwStream.Read(buffer, 0, client.ReceiveBufferSize); //Getting data in Bytes from Python
        string dataReceived = Encoding.UTF8.GetString(buffer, 0, bytesRead); //Converting byte data to string

        if (dataReceived != null)
        {
            //---Using received data---
            receivedData = StringToArray(dataReceived); //<-- assigning receivedPos value from Python
        }
    }

    public static float[] StringToArray(string sVector)
    {
        // Remove the parentheses
        if (sVector.StartsWith("[") && sVector.EndsWith("]"))
        {
            sVector = sVector.Substring(1, sVector.Length - 2);
        }

        // split the items
        string[] sArray = sVector.Split(',');

        // store as a float[] 
        float[]  result = new float[23];

        for(int i=0; i<23; i++){
            result[i] = float.Parse(sArray[i])/1000;
        }
        return result;
    }
}