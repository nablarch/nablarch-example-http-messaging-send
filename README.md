nablarch-example-http-messaging-send
======================================

Nablarch FrameworkのHTTPメッセージングの送信側のExampleです。
HTTPメッセージングの受信側のExampleと組み合わせて使用します。

## 実行手順

### 1.動作環境
実行環境に以下のソフトウェアがインストールされている事を前提とします。
* Java Version : 17
* Maven 3.9.9以降

なお、このアプリケーションはH2 Database Engineを組み込んでいます。別途DBサーバのインストールは必要ありません。

### 2. プロジェクトリポジトリの取得
Gitを使用している場合、アプリケーションを配置したいディレクトリにて「git clone」コマンドを実行してください。
以下、コマンドの例です。

    $mkdir c:\example
    $cd c:\example
    $git clone https://github.com/nablarch/nablarch-example-http-messaging-send.git 

### 3. アプリケーションのビルド
#### 3.1. アプリケーションのビルド
アプリケーションをビルドします。以下のコマンドを実行してください。

    $mvn clean package

実行に成功すると、以下のようなログがコンソールに出力されます。

    (中略)
    [INFO] ------------------------------------------------------------------------
    [INFO] BUILD SUCCESS
    [INFO] ------------------------------------------------------------------------
    (中略)

#### データベースのセットアップ及びエンティティクラスの作成について

アプリケーションを実行するためにはデータベースのセットアップ及びエンティティクラスの作成が必要ですが、これは`mvn package`の実行に含まれています。
この処理は`mvn generate-resources`で個別に実行することもできます。

※gspプラグインをJava 17で実行するためにはJVMオプションの指定が必要ですが、そのオプションは`.mvn/jvm.config`で指定しています。

### 4. アプリケーションの起動

先にHTTPメッセージングの受信側のExampleを起動しておいてください。

以下のコマンドで、データベースの状態を最新化、HTTPメッセージングの送信側のExampleを起動します。

    $mvn generate-resources
    $mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main -Dexec.args="'-diConfig' 'classpath:http-messaging-send-boot.xml' '-requestPath' 'ProjectSaveMessageAction' '-userId' 'batch_user'"
    
なお、 `maven-assembly-plugin` を使用して実行可能jarの生成を行っているため、以下の手順にて実行することもできる。

1. ``target/application-<version_no>.zip`` を任意のディレクトリに解凍する。
2. 以下のコマンドにて実行する

  ```
      java -jar <1で解凍したディレクトリ名>/nablarch-example-http-messaging-send-<version_no>.jar -diConfig classpath:http-messaging-send-boot.xml -requestPath ProjectSaveMessageAction -userId batch_user
  ```
    

起動に成功すると、HTTPメッセージングの受信側との通信を行います。
送信側のアプリケーションログが以下のように出力されます。


```log
2023-02-15 15:48:09.536 -INFO- nablarch.fw.launcher.Main [null] boot_proc = [] proc_sys = [http-messaging-send] req_id =
[null] usr_id = [null] @@@@ APPLICATION SETTINGS @@@@
        system settings = {
        }
        business date = [20140123]
2023-02-15 15:48:09.556 -INFO- com.nablarch.example.ProjectSaveMessageAction [202302151548095560002] boot_proc = [] proc_
sys = [http-messaging-send] req_id = [ProjectSaveMessageAction] usr_id = [batch_user] start
2023-02-15 15:48:09.583 -INFO- MESSAGING [202302151548095560002] boot_proc = [] proc_sys = [http-messaging-send] req_id =
 [ProjectSaveMessageAction] usr_id = [batch_user] @@@@ HTTP SENT MESSAGE @@@@
        thread_name    = [pool-1-thread-1]
        message_id     = [null]
        destination    = [POST http://localhost:9080/ProjectSaveAction]
        correlation_id = [null]
        message_header = [{X-Message-Id=1, Destination=POST http://localhost:9080/ProjectSaveAction}]
        message_body   = [{"projectName":"プロジェクト００１","projectType":"development","projectClass":"s","projectStar
tDate":"20100918","projectEndDate":"20150409","clientId":1,"projectManager":"鈴木","projectLeader":"佐藤","note":"備考欄"
,"sales":10000,"costOfGoodsSold":1000,"sga":2000,"allocationOfCorpExpenses":3000}]
2023-02-15 15:48:10.422 -INFO- MESSAGING [202302151548095560002] boot_proc = [] proc_sys = [http-messaging-send] req_id =
 [ProjectSaveMessageAction] usr_id = [batch_user] @@@@ HTTP RECEIVED MESSAGE @@@@
        thread_name    = [pool-1-thread-1]
        message_id     = [null]
        destination    = [null]
        correlation_id = [null]
        message_header = [{=HTTP/1.1 201 Created, Transfer-Encoding=chunked, Server=Jetty(12.0.0.alpha3), X-Correlation-I
d=1, STATUS_CODE=201, Date=Wed, 15 Feb 2023 06:48:09 GMT, Content-Type=application/json;charset=UTF-8}]
        message_body   = [{"statusCode":"201"}]
2023-02-15 15:48:10.443 -INFO- nablarch.fw.handler.MultiThreadExecutionHandler [202302151548095370001] boot_proc = [] pro
c_sys = [http-messaging-send] req_id = [ProjectSaveMessageAction] usr_id = [batch_user]
Thread Status: normal end.
Thread Result:[200 Success] The request has succeeded.
2023-02-15 15:48:10.445 -INFO- nablarch.core.log.app.BasicCommitLogger [202302151548095370001] boot_proc = [] proc_sys =
[http-messaging-send] req_id = [ProjectSaveMessageAction] usr_id = [batch_user] TOTAL COMMIT COUNT = [1]
2023-02-15 15:48:10.447 -INFO- nablarch.fw.launcher.Main [null] boot_proc = [] proc_sys = [http-messaging-send] req_id =
[null] usr_id = [null] @@@@ END @@@@ exit code = [0] execute time(ms) = [1373]
```

ログ出力後、本Exampleは自動的に終了します。
