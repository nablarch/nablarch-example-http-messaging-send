nablarch-example-http-messaging-send
======================================
Nablarch FrameworkのHTTPメッセージングの送信側のExampleです。
HTTPメッセージングの受信側のExampleと組み合わせて使用します。

## 実行手順

### 1.動作環境
実行環境に以下のソフトウェアがインストールされている事を前提とします。
* Java Version : 8
* Maven 3.0.5以降

なお、このアプリケーションはH2 Database Engineを組み込んでいます。別途DBサーバのインストールは必要ありません。

### 2. プロジェクトリポジトリの取得
Gitを使用している場合、アプリケーションを配置したいディレクトリにて「git clone」コマンドを実行してください。
以下、コマンドの例です。

    $mkdir c:\example
    $cd c:\example
    $git clone https://github.com/nablarch/nablarch-example-http-messaging-send.git 

### 3. アプリケーションのビルド
#### 3.1. データベースのセットアップ及びエンティティクラスの作成
まず、データベースのセットアップ及びエンティティクラスの作成を行います。以下のコマンドを実行してください。

    $cd nablarch-example-http-messaging-send
    $mvn -P gsp clean generate-resources
    $mvn -P gsp install:install-file

#### 3.2. アプリケーションのビルド
次に、アプリケーションをビルドします。以下のコマンドを実行してください。

    $mvn clean package

### 4. アプリケーションの起動

先にHTTPメッセージングの受信側のExampleを起動しておいてください。

以下のコマンドで、HTTPメッセージングの送信側のExampleが起動します。

    $mvn -P gsp gsp-dba:import-schema
    $mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main -Dexec.args="'-diConfig' 'classpath:http-messaging-send-boot.xml' '-requestPath' 'ProjectSaveMessageAction' '-userId' 'batch_user'"
    
なお、 `maven-assembly-plugin` を使用して実行可能jarの生成を行っているため、以下の手順にて実行することもできる。

1. ``target/application-<version_no>.zip`` を任意のディレクトリに解凍する。
2. 以下のコマンドにて実行する

  ```
      java -jar <1で解凍したディレクトリ名>/nablarch-example-http-messaging-send-<version_no>.jar -diConfig classpath:http-messaging-send-boot.xml -requestPath ProjectSaveMessageAction -userId batch_user
  ```
    

起動に成功すると、HTTPメッセージングの受信側との通信を行います。
送信側のアプリケーションログが以下のように出力されます。


    2016-07-13 16:18:12.579 -INFO- ROO [null] @@@@ APPLICATION SETTINGS @@@@
            system settings = {
            }
            business date = [20140123]
    2016-07-13 16:18:12.603 -INFO- ROO [201607131618126030002] start
    2016-07-13 16:18:12.666 -INFO- ROO [201607131618126030002] @@@@ HTTP SENT MESSAGE @@@@
            thread_name    = [pool-1-thread-1]
            message_id     = [null]
            destination    = [POST http://localhost:9080/ProjectSaveAction]
            correlation_id = [null]
            message_header = [{X-Message-Id=1, Destination=POST http://localhost:9080/ProjectSaveAction}]
            message_body   = [{"projectName":"プロジェクト００１","projectType":"development","projectClass":"s",
                              "projectStartDate":"20100918","projectEndDate":"20150409","clientId":"1",
                              "projectManager":"鈴木","projectLeader":"佐藤","userId":"100","note":"備考欄",
                              "sales":"10000","costOfGoodsSold":"1000","sga":"2000","allocationOfCorpExpenses":"3000"}]
    2016-07-13 16:18:13.633 -INFO- ROO [201607131618126030002] @@@@ HTTP RECEIVED MESSAGE @@@@
            thread_name    = [pool-1-thread-1]
            message_id     = [null]
            destination    = [null]
            correlation_id = [null]
            message_header = [{=HTTP/1.1 201 Created, Transfer-Encoding=chunked, X-Frame-Options=SAMEORIGIN, Server=Apache-Coyote/1.1,
                              X-Correlation-Id=1, STATUS_CODE=201, Date=Wed, 13 Jul 2016 07:18:13 GMT, Content-Type=application/json;charset=UTF-8}]
            message_body   = [{"statusCode":"201"}]
    2016-07-13 16:18:13.657 -INFO- ROO [201607131618125800001]
            Thread Status: normal end.
            Thread Result:[200 Success] The request has succeeded.
    2016-07-13 16:18:13.658 -INFO- ROO [201607131618125800001] TOTAL COMMIT COUNT =[1]
    2016-07-13 16:18:13.659 -INFO- ROO [201607131618125800001] @@@@ END @@@@ exit code = [0] execute time(ms) = [1789]

ログ出力後、本Exampleは自動的に終了します。
