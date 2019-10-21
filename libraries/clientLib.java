/*
Library to assist with the socket connection and JSON formatting
*/

import java.net.*;
import java.io.*;
import org.json.*;

public class socketConnection{
  private Socket sock = null;

  public Socket connect(String address, int port)
  {
    try{
      sock = new Socket(address, port);
    }
    return sock;
  }
  public void send(Socket sock, JSONObject data)
  {
    // TODO
  }

  public String receive(Socket sock)
  {
    in = new DataOutputStream(new BufferedInputStream(sock.getOutputStream()));
    try{
      String message = in.readUTF();
    catch(IOException i){
      continue;
    }
    return message;
  }

  public JSONObject format(String data)
  {
    JSONObject jdata = new JSONObject(data);
    return jdata;
  }
  public String unformat(JSONObject jdata)
}
