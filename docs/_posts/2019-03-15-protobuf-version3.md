
# protobuf - version 3
本指南介绍了如何使用协议缓冲区语言来构建你的协议缓冲区数据，包括.proto文件语法以及如何从你的.proto文件中生成数据访问类。它涵盖了proto3版本的协议缓冲区语言：关于proto2语法的信息，请参阅Proto2语言指南。

这是一个参考指南--关于使用本文档中描述的许多功能的逐步示例，请参见您所选择的语言的教程（目前只有proto2；更多的proto3文档即将推出）。
## Defining A Message Type
首先我们来看一个很简单的例子。假设你想定义一个搜索请求的消息格式，每个搜索请求都有一个查询字符串，你感兴趣的特定结果页面，以及每页的结果数量。下面是你用来定义消息类型的.proto文件。

```python
syntax = "proto3";

message SearchRequest {
  string query = 1;
  int32 page_number = 2;
  int32 result_per_page = 3;
}
```
- 文件的第一行指定你正在使用proto3语法：如果你不这样做，协议缓冲区编译器会认为你正在使用proto2。**这必须是文件的第一行非空，非注释。**
- SearchRequest消息定义指定了三个字段(名/值对)，每个字段用于你想包含在这种类型的消息中的数据。每个字段都有一个名称和一个类型。
### 指定字段类型
在上面的例子中，所有的字段都是scalar类型：两个整数（page_number和result_per_page）和一个字符串（query）。然而，你也可以为你的字段指定复合类型，包括枚举和其他消息类型。_

> double 类型 - python： float ； golang： float64
> float 类型 - python： float；golang： float32
> int32 ：python：int；golang：int32
> int64: python：int；golang：int64
> uint32: python： int ；golang： uint32
> uint64: python： int ；golang： uint64
> sint32: python int；golang： int32
> sint64: python：int；golang：int64
> fixed32: python： int ；golang： uint32
> fixed64: python： int ；golang： uint64
> sfixed32: python： int ；golang： int32
> sfixed64: python： int ；golang： int64
> bool： python： bool；golang：bool
> string： python：str/unicode ；golang：string
> bytes： python：str；golang：[]bytes

### 分配字段号
如你所见，**消息定义中的每个字段都有一个独特的编号**。这些字段号用于在消息二进制格式中识别你的字段，一旦你的消息类型被使用，就不应该被改变。请注意，**范围1到15的字段号需要一个字节来编码，包括字段号和字段的类型。16到2047范围内的字段号需要两个字节。所以你应该把数字1到15保留给非常频繁出现的消息元素。**记住要为将来可能添加的频繁出现的元素留出一些空间。

您可以指定的最小字段号是1，最大的字段号是2^29-1，或536,870,911。你也不能使用数字19000到19999(FieldDescriptor::kFirstReservedNumber到FieldDescriptor::kLastReservedNumber)，因为它们是为协议缓冲区的实现保留的--如果你在你的.proto中使用这些保留的数字之一，协议缓冲区编译器会抱怨。同样，你也不能使用任何之前保留的字段号。
### 指定字段规则
消息字段可以是以下之一。

singular：一个格式良好的消息可以有0个或1个这样的字段（但不能多于一个）。而这是proto3语法的默认字段规则。
repeated：这个字段可以在一个格式良好的消息中重复任何次数（包括零）。重复值的顺序将被保留。
在proto3中，标量数字类型的重复字段默认使用打包编码。

### 添加注释
支持c++风格的两种注释方式 
```Protobuf
/* SearchRequest represents a search query, with pagination options to
 * indicate which results to include in the response. */

message SearchRequest {
  string query = 1;
  int32 page_number = 2;  // Which page number do we want?
  int32 result_per_page = 3;  // Number of results to return per page.
}
```

### 预留字段
如果你通过完全删除一个字段或注释来更新消息类型，未来的用户在对该类型进行更新时可以重新使用字段号。如果他们以后加载同一.proto的旧版本，这可能会导致严重的问题，包括数据损坏、隐私错误等。确保这种情况不会发生的一种方法是指定保留你删除字段的字段号（和/或名称，这也会导致JSON序列化的问题）。如果未来的任何用户试图使用这些字段标识符，协议缓冲区编译器会抱怨。
```Protobuf
message Foo {
  reserved 2, 15, 9 to 11;
  reserved "foo", "bar";
}
```

### 缺省值
> strings: “”
> bytes: empty bytes
> bools: false
> numeric types: 0
> enums: first defined enum value, which must be 0

如果字段被设置成缺省值，该字段在传递时不会被传递
你可以在定义消息时置顶字段的缺省值。
```Protobuf
optional int32 result_per_page = 3 [default = 10];
```

### 支持消息嵌套
```Protobuf

message SearchResponse {
  repeated Result result = 1;
}

message Result {
  required string url = 1;
  optional string title = 2;
  repeated string snippets = 3;
}
```

### 导入定义
在上面的例子中，Result消息类型被定义在与SearchResponse相同的文件中--如果你想作为字段类型使用的消息类型已经被定义在另一个.proto文件中，那该怎么办？

你可以通过导入其他.proto文件的定义来使用它们。要导入另一个.proto的定义，你可以在文件的顶部添加一个导入语句。
```Protobuf
import "myproject/other_protos.proto";
```
默认情况下，您只能使用直接导入的.proto文件中的定义。然而，有时您可能需要将.proto文件移动到一个新的位置。与其直接移动.proto文件并在一次更改中更新所有的调用站点，现在您可以在旧位置放置一个虚拟的.proto文件，以使用import public概念将所有的导入转发到新位置。 import public依赖可以被任何导入包含import public声明的proto的人中转依赖。例如
```Protobuf
// new.proto
// All definitions are moved here
```

```Protobuf
// old.proto
// This is the proto that all clients are importing.
import public "new.proto";
import "other.proto";
```

```Protobuf
// old.proto
// This is the proto that all clients are importing.
import public "new.proto";
import "other.proto";
```
协议编译器使用-I/--proto_path标志在协议编译器命令行指定的一组目录中搜索导入的文件。如果没有给出标志，则在编译器被调用的目录中查找。一般来说，你应该将--proto_path标志设置为项目的根目录，并且对所有的导入文件使用完全限定的名称。

### 使用proto3信息类型
可以导入proto3消息类型并在proto2消息中使用它们，反之亦然。然而，proto2枚举不能用于proto3语法中。

### 嵌套类型
你可以在其他消息类型中定义和使用消息类型，就像下面的例子--这里的Result消息被定义在SearchResponse消息中。
```Protobuf
message SearchResponse {
  message Result {
    required string url = 1;
    optional string title = 2;
    repeated string snippets = 3;
  }
  repeated Result result = 1;
}
```

如果你想在它的父消息类型之外重用这个消息类型，你把它称为_Parent_._Type_
```Protobuf
message SomeOtherMessage {
  optional SearchResponse.Result result = 1;
}
```

你可以随心所欲地深度嵌套信息。
```Protobuf
message Outer {       // Level 0
  message MiddleAA {  // Level 1
    message Inner {   // Level 2
      required int64 ival = 1;
      optional bool  booly = 2;
    }
  }
  message MiddleBB {  // Level 1
    message Inner {   // Level 2
      required int32 ival = 1;
      optional bool  booly = 2;
    }
  }
}
```

### 更新信息类型
如果现有的消息类型不再满足您的所有需求--例如，您希望消息格式有一个额外的字段--但您仍然希望使用旧的格式创建的代码，不用担心！您可以在不破坏任何现有代码的情况下更新消息类型。在不破坏任何现有代码的情况下更新消息类型是非常简单的。只要记住以下规则即可。
- 不要改变任何现有字段的字段号。
- 你添加的任何新字段应该是可选的或重复的。这意味着任何使用 "旧的 "消息格式的代码序列化的消息都可以被新生成的代码解析，因为它们不会缺少任何必需的元素。你应该为这些元素设置合理的默认值，这样新代码就可以与旧代码生成的消息进行正确的交互。同样，你的新代码创建的消息也可以被你的旧代码解析：旧的二进制文件在解析时只是忽略新的字段。但是，未知字段不会被丢弃，如果消息后来被序列化，未知字段也会一起序列化--所以如果消息被传递给新代码，新字段仍然可用。
- 非必填字段可以被删除，只要字段号在你更新的消息类型中不被再次使用。您可能想要重新命名该字段，也许可以添加前缀 "OBSOLETE_"，或者保留该字段号(reserved)，这样您的.proto的未来用户就不会意外地重复使用该字段号。
- 一个非必填字段可以转换为extension，反之亦然，只要类型和编号保持不变。
- int32、uint32、int64、uint64和bool都是兼容的--这意味着你可以将一个字段从这些类型中的一个改成另一个，而不会破坏向前或向后的兼容性。如果从线上解析出一个不适合相应类型的数字，你将得到与在C++中把数字投到该类型中一样的效果（例如，如果一个64位的数字被读作int32，它将被截断为32位）。
- sint32和sint64是相互兼容的，但与其他整数类型不兼容。
- string和字节是兼容的，只要字节是有效的UTF-8。
- 如果字节包含了消息的编码版本，则嵌入式消息与字节兼容。
- fixed32与sfixed32兼容，fixed64与sfixed64兼容。
- 对于字符串、字节和消息字段，option与repeat兼容。给定的repeated字段的序列化数据作为输入，如果客户端期望它是repeated字段，如果是基元类型字段，客户端将取最后一个输入值，如果是消息类型字段，则合并所有输入元素。请注意，这对于数值类型，包括bools和enums，一般来说并不安全。数值类型的重复字段可以以packed格式序列化，当期望使用可选字段时，它将不会被正确解析。
- 改变默认值一般来说是可以的，只要你记住默认值永远不会通过线路发送。因此，如果一个程序收到了一个没有设置特定字段的消息，该程序将看到默认值，因为它是在该程序的协议版本中定义的。它不会看到发件人代码中定义的默认值。
- enum与int32、uint32、int64和uint64在线格式上是兼容的（注意，如果值不适合，会被截断），但要注意，当消息被反序列化时，客户端代码可能会以不同的方式处理它们。值得注意的是，当消息被反序列化时，未被识别的枚举值会被丢弃，这使得字段的has...访问器返回false，其getter返回枚举定义中列出的第一个值，如果指定了一个值，则返回默认值。在重复枚举字段的情况下，任何未识别的值都会从列表中剥离出来。然而，整数字段将始终保留其值。正因为如此，在将整数字段升级为枚举字段时，你需要非常小心，以免在线路上接收到越界的枚举值。
- 在当前的Java和C++实现中，当未识别的枚举值被剥离出来时，它们会与其他未知字段一起存储。请注意，如果这些数据被序列化，然后被识别这些值的客户端重新解析，这会导致奇怪的行为。在可选字段的情况下，即使在原始消息被反序列化后写入了一个新的值，旧的值仍然会被识别它的客户端读取。在重复字段的情况下，旧值将出现在任何已识别的值和新添加的值之后，这意味着顺序将不会被保留。
- 将一个可选值改成一个新的oneof的成员是安全的，二进制兼容的。如果你确定一次没有代码集超过一个，那么将多个可选字段移动到一个新的oneof中可能是安全的。将任何字段移动到一个现有的oneof中是不安全的。
- 在map\<K，V\>和相应的重复消息字段之间更改字段是二进制兼容的（关于消息布局和其他限制，请参见下面的Maps）。然而，改变的安全性取决于应用：当反序列化和重新序列化消息时，使用重复字段定义的客户端将产生语义上相同的结果；然而，使用map字段定义的客户端可能会对条目进行重新排序，并放弃有重复键的条目。
### 扩展
扩展名可以让你声明消息中的一系列字段号可供第三方扩展。扩展名是一个字段的占位符，它的类型不是由原来的.proto文件定义的，这允许其他.proto文件通过定义这些字段的部分或全部类型来添加到你的消息定义中。让我们来看一个例子：
```Protobuf
message Foo {
  // ...
  extensions 100 to 199;
}
```
这表示Foo中字段号[100, 199]()的范围是为扩展名保留的. 其他用户现在可以在他们自己的.proto文件中向Foo添加新的字段，导入你的.proto，使用你指定范围内的字段号--例如:
```Protobuf
extend Foo {
  optional int32 bar = 126;
}
```
这将在Foo的原始定义中添加一个名为bar的字段，字段号为126。

当你的用户的Foo消息被编码后，传输格式与用户在Foo内部定义新字段完全一样。然而，在你的应用程序代码中访问扩展字段的方式与访问常规字段的方式略有不同--你生成的数据访问代码有特殊的访问器用于处理扩展字段。所以，举例来说，下面是在C++中设置bar值的方法。
```Protobuf
Foo foo;
foo.SetExtension(bar, 15);
```

同样，Foo类定义了模板化的访问器HasExtension()，ClearExtension()，GetExtension()，MutableExtension()和AddExtension()。所有这些访问符的语义都与普通字段的相应生成访问符相匹配。关于使用扩展的更多信息，请参见您所选择的语言的生成代码参考。

请注意，扩展可以是任何字段类型，包括消息类型，但不能是oneofs或maps。

### Nested Extensions
你可以在另一个类型的范围内声明扩展。
```Protobuf
message Baz {
  extend Foo {
    optional int32 bar = 126;
  }
  ...
}
```

在这种情况下，访问该扩展的C++代码是：
```Protobuf
Foo foo;
foo.SetExtension(Baz::bar, 15);
```
换句话说，唯一的影响是，bar被定义在Baz的范围内。

这里很容易造成混淆。声明一个嵌套在消息类型中的扩展块并不意味着外部类型和扩展类型之间有任何关系。也就是说，上面的例子并不意味着Baz是Foo的任何子类。它的意思是，bar被声明在Baz的作用域内，它只是一个静态成员。
一个常见的模式是在扩展的字段类型的作用域内定义扩展--例如，这里是对Baz类型的Foo的扩展，其中扩展被定义为Baz的一部分。
```Protobuf
message Baz {
  extend Foo {
    optional Baz foo_ext = 127;
  }
  ...
}
```

但是，并没有要求在该类型中定义一个带有消息类型的扩展。你也可以这样做
```Protobuf
message Baz {
  ...
}

// This can even be in a different file.
extend Foo {
  optional Baz foo_baz_ext = 127;
}
```
事实上，为了避免混淆，可以首选这种语法。如上所述，嵌套语法经常被还不熟悉扩展的用户误认为是子类。

### Choosing Extension Numbers
确保两个用户不使用相同的字段号向同一消息类型添加扩展名是非常重要的--如果扩展名被意外地解释为错误的类型，会导致数据损坏。你可能需要考虑为你的项目定义一个扩展号约定来防止这种情况发生。

如果您的编号约定可能涉及到字段号非常大的扩展，您可以使用 max 关键字指定您的扩展范围上升到最大可能的字段号。
```Protobuf
message Foo {
  extensions 1000 to max;
}
```
max is 229 - 1, 或 536,870,911.
如同一般选择字段号一样，你的编号约定也需要避免字段号19000到19999（FieldDescriptor::kFirstReservedNumber到FieldDescriptor::kLastReservedNumber），因为它们是为协议缓冲区的实现保留的。您可以定义一个包括这个范围的扩展范围，但协议编译器不允许您用这些数字定义实际的扩展。
### Oneof
如果你的消息中有许多可选字段，而且最多只能同时设置一个字段，你可以通过使用oneof功能来强制这种行为并节省内存。

Oneof字段和可选字段一样，只是oneof中的所有字段都共享内存，而且最多可以同时设置一个字段。设置oneof中的任何一个成员都会自动清除其他所有成员。你可以使用case()或WhichOneof()方法检查oneof中的哪个值被设置了（如果有的话），这取决于你选择的语言。
#### using One of
要在你的.proto中定义一个oneof，你可以使用oneof关键字，后面跟上你的oneof名称，本例中是test_oneof。
```Protobuf
message SampleMessage {
  oneof test_oneof {
     string name = 4;
     SubMessage sub_message = 9;
  }
}
```
然后你可以在oneof定义中添加你的oneof字段. 你可以添加任何类型的字段，但不能使用 required、optional 或重复的关键字。如果你需要在oneof中添加一个重复的字段，你可以使用一个包含重复字段的消息。

在你生成的代码中，oneof字段的获取器和设置器与常规的可选方法相同。你还可以得到一个特殊的方法来检查oneof中的哪个值（如果有的话）被设置了。你可以在相关的API参考中找到更多关于你所选择的语言的oneof API的信息。

#### Oneof Features
设置一个oneof字段会自动清除oneof的所有其他成员。因此，如果你设置了几个oneof字段，只有最后一个字段的值还会存在。
```Protobuf
SampleMessage message;
message.set_name("name");
CHECK(message.has_name());
message.mutable_sub_message();   // Will clear name field.
CHECK(!message.has_name());
```

-  如果解析器在线路上遇到同一个oneof的多个成员，那么在解析的消息中只使用最后一个成员。
- oneof不支持扩展。
- 一个oneof不能重复。
- 反射API适用于oneof字段。
- 如果你将一个oneof字段设置为默认值（比如将一个int32的oneof字段设置为0），该oneof字段的 "case "将被设置，并且该值将在线上被序列化。
- 如果你使用的是C++，请确保你的代码不会导致内存崩溃。下面的示例代码会因为调用set_name()方法已经删除了sub_message而导致崩溃。
```Protobuf
SampleMessage message;
SubMessage* sub_message = message.mutable_sub_message();
message.set_name("name");      // Will delete sub_message
sub_message->set_...            // Crashes here
```
同样在C++中，如果用swap()两个带有oneofs的消息，每个消息最后都会用对方的oneof情况：在下面的例子中，msg1会有一个sub_message，msg2会有一个name。_
```Protobuf
SampleMessage msg1;
msg1.set_name("name");
SampleMessage msg2;
msg2.mutable_sub_message();
msg1.swap(&msg2);
CHECK(msg1.has_sub_message());
CHECK(msg2.has_name());
```

#### 向后兼容性问题
在添加或删除oneof字段时要小心。如果检查oneof的值返回None/NOT_SET，这可能意味着oneof没有被设置，或者它被设置为不同版本的oneof中的字段。没有办法分辨两者的区别，因为没有办法知道线上的未知字段是否是oneof的成员。_

#### 标签再利用问题
将可选字段移入或移出oneof。在电文被序列化和解析后，你可能会丢失一些信息（一些字段将被清除）。但是，您可以安全地将一个字段移入一个新的oneof中，如果知道只有一个字段被设置，您也可以将多个字段移入。
删除一个oneof字段并将其添加回来。这可能会在消息被序列化和解析后清除你当前设置的oneof字段。
拆分或合并oneof。这和移动普通的可选字段有类似的问题。
### maps
If you want to create an associative map as part of your data definition, protocol buffers provides a handy shortcut syntax:
```Protobuf
map<key_type, value_type> map_field = N;
```
...其中key_type可以是任何积分或字符串类型(所以，除了浮点类型和字节以外，任何标量类型)。注意，enum不是有效的key_type。value_type可以是任何类型，除了另一个map。

所以，举例来说，如果你想创建一个Project消息的map，其中每个Project消息都与一个字符串键相关联，你可以这样定义它。
```Protobuf
map<string, Project> projects = 3;
```

#### Maps功能
- Maps不支持Extensions。
- Maps不支持repeated、optional或required。
- Maps不保序。
- 为.proto生成文本格式时，Maps按键排序。数字键是按数字排序的。
- 当从线上解析或合并时，如果有重复的Maps键，则使用最后一个键。当从文本格式解析Maps时，如果有重复的键，解析可能会失败。
#### 向后兼容
映射语法相当于线上的以下内容，所以不支持映射的协议缓冲区实现仍然可以处理你的数据。

任何支持map的协议缓冲器实现都必须同时产生和接受上述定义所能接受的数据。
### Packages
您可以在.proto文件中添加一个可选的包指定符，以防止协议消息类型之间的名称冲突。
```Protobuf
package foo.bar;
message Open { ... }
```
然后你可以在定义你的消息类型的字段时使用包指定器。
```Protobuf
message Foo {
  ...
  required foo.bar.Open open = 1;
  ...
}
```
包指定符对生成代码的影响方式取决于你所选择的语言。

- 在C++中，生成的类被封装在一个C++命名空间中。例如，Open将在命名空间foo::bar中。
- 在Java中，包被用作Java包，除非你在你的.proto文件中明确提供了一个选项java_package。
- 在 Python 中，包指令被忽略，因为 Python 模块是根据它们在文件系统中的位置来组织的。
- 在Go中，包指令被忽略，生成的.pb.go文件在对应的go_proto_library规则后命名的包中。
需要注意的是，即使包指令不直接影响生成的代码，例如在Python中，仍然强烈建议为.proto文件指定包，否则可能会导致描述符的命名冲突，使proto不能移植到其他语言中。
### 定义服务
如果你想在RPC（远程过程调用）系统中使用你的消息类型，你可以在.proto文件中定义一个RPC服务接口，协议缓冲编译器将用你选择的语言生成服务接口代码和存根。所以，举例来说，如果你想定义一个RPC服务，它的方法是接受你的SearchRequest并返回SearchResponse，你可以在你的.proto文件中定义如下。

```Protobuf
service SearchService {
  rpc Search(SearchRequest) returns (SearchResponse);
}
```
gRPC是与协议缓冲区配合使用的最直接的RPC系统：一个由Google开发的语言和平台中立的开源RPC系统。gRPC与协议缓冲区配合得特别好，它可以让你使用一个特殊的协议缓冲区编译器插件直接从你的.proto文件中生成相关的RPC代码。

如果你不想使用gRPC，也可以用自己的RPC实现来使用协议缓冲区。你可以在Proto2语言指南中找到更多关于这方面的信息。

还有一些正在进行的第三方项目来开发协议缓冲区的RPC实现。关于我们知道的项目链接列表，请参见[第三方附加组件维基页面][2]。

### JSON Mapping
Proto3支持JSON的规范编码，使系统之间更容易共享数据。下表按类型对编码进行了描述。

如果JSON编码的数据中缺少一个值，或者其值为空，那么在解析到协议缓冲区时，将被解释为合适的默认值。如果一个字段在协议缓冲区中具有默认值，那么它将在JSON编码数据中被默认省略，以节省空间。实现可以提供选项，在JSON编码输出中发出具有默认值的字段。
> message
> > object
> > {"fooBar": v, "g": null, …}
> > 生成JSON对象。消息字段名被映射为 lowerCamelCase 并成为 JSON 对象键。如果指定了json_name字段选项，指定的值将被用作键。解析器既接受 lowerCamelCase 名称（或 json_name 选项指定的名称），也接受原始的原字段名。null 是所有字段类型的可接受值，并被视为相应字段类型的默认值。
> enum
> > string
> > "FOO_BAR"_
> > 使用proto中指定的枚举值的名称。解析器同时接受枚举名和整数值。

#### JSON options
proto3 JSON实现可以提供以下选项。

- 省略带有默认值的字段。在proto3 JSON输出中，默认省略了带有默认值的字段。一个实现可以提供一个选项来覆盖这个行为，并输出默认值的字段。
- 忽略未知字段。Proto3 JSON解析器默认拒绝未知字段，但可以提供一个选项在解析时忽略未知字段。
- 使用proto字段名代替 lowerCamelCase名：默认情况下，proto3 JSON打印机应该将字段名转换为 lowerCamelCase，并将其作为JSON名。一个实现可以提供一个选项来使用proto字段名作为JSON名。Proto3 JSON解析器需要同时接受转换后的 lowerCamelCase名称和proto字段名称。
- 将枚举值作为整数而不是字符串排放。JSON输出中默认使用枚举值的名称。我们可以提供一个选项来使用枚举值的数值来代替。
### Options
.proto 文件中的单个声明可以用一些选项来注释。选项不会改变声明的整体含义，但可能会影响它在特定上下文中的处理方式。可用选项的完整列表定义在google/protobuf/descriptor.proto中。

有些选项是文件级选项，这意味着它们应该被写在顶层作用域，而不是在任何消息、枚举或服务定义中。有些选项是消息级选项，这意味着它们应该被写在消息定义中。有些选项是字段级选项，这意味着它们应该被写在字段定义中。选项也可以写在枚举类型、枚举值、oneof 字段、服务类型和服务方法上；但是，目前还没有针对这些类型的有用选项。

下面是一些最常用的选项。
- java_package (文件选项): 你想为你生成的Java类使用的包。如果在.proto文件中没有给出明确的java_package选项，那么默认将使用proto包（在.proto文件中使用 "package "关键字指定）。然而，proto包一般不会成为好的Java包，因为proto包不应该以反向域名开始。如果不生成Java代码，这个选项没有效果。
```Protobuf
option java_package = "com.example.foo";
```
- java_multiple_files（文件选项）。使顶层的消息、枚举和服务在包的级别上被定义，而不是在以.proto文件命名的外层类中。
```Protobuf
option java_multiple_files = true;
```
- java_outer_classname（文件选项）。你想生成的最外层Java类的类名（也就是文件名）。如果在.proto文件中没有指定明确的java_outer_classname，那么类名将通过将.proto文件名转换为驼峰大写来构建（所以foo_bar.proto变成FooBar.java）。如果不生成Java代码，这个选项没有效果。_
```Protobuf
option java_outer_classname = "Ponycopter";
```
- optimize_for (文件选项).可以设置为 SPEED, CODE_SIZE, 或 LITE_RUNTIME: 可以设置为SPEED、CODE_SIZE或LITE_RUNTIME。这将以下列方式影响C++和Java代码生成器（可能还有第三方生成器）。

> > SPEED（默认）。协议缓冲区编译器将生成用于序列化、解析和对你的消息类型执行其他常见操作的代码。这个代码是高度优化的。
> > CODE_SIZE：协议缓冲编译器将生成最小的类，并将依靠共享的、基于反射的代码来实现序列化、解析和其他各种操作。因此，生成的代码将比使用SPEED时小得多，但操作会更慢。类仍然会实现与SPEED模式下完全相同的公共API。这种模式在包含大量.proto文件的应用程序中最有用，而且不需要所有的文件都快得惊人。
> > LITE_RUNTIME模式。协议缓冲区编译器将生成只依赖于 "精简 "运行库的类（libprotobuf-lite而不是libprotobuf）。精简运行时比完整库小得多（大约小一个数量级），但省略了某些功能，如描述符和反射。这对于在手机等受限平台上运行的应用程序特别有用。编译器仍然会像在SPEED模式下一样，快速生成所有方法的实现。生成的类将只实现每个语言中的MessageLite接口，它只提供了完整的Message接口的方法子集。_
```Protobuf
option optimize_for = CODE_SIZE;
```
> > cc_enable_arenas (文件选项): 为C++生成的代码开启竞技场分配功能。
> > objc_class_prefix (文件选项): 设置Objective-C类的前缀，该前缀被用于所有从这个.proto生成的Objective-C类和枚举。没有默认值。你应该使用 Apple 推荐的介于 3-5 个大写字符之间的前缀。请注意，所有2个字母的前缀都被Apple保留。
> > deprecated (字段选项)。如果设置为 "true"，表示该字段已被废弃，新代码不应使用。在大多数语言中，这没有实际效果。在Java中，这变成了一个@Deprecated注解。将来，其他特定语言的代码生成器可能会在字段的访问器上生成废弃注解，这将在编译试图使用该字段的代码时引起警告。如果这个字段没有被任何人使用，而你又想阻止新用户使用它，可以考虑用一个保留的语句来代替字段声明。
```Protobuf
int32 old_field = 6 [deprecated = true];
```
#### 自定义选项
协议缓冲区还允许您定义和使用自己的选项。这是一个大多数人不需要的高级功能。如果您认为确实需要创建自己的选项，请参见 Proto2 语言指南了解详情。请注意，创建自定义选项会使用扩展，而扩展只允许在proto3中使用自定义选项。

### Generating Your Classes
要生成Java、Python、C++、Go、Ruby、Objective-C或C#代码，你需要使用.proto文件中定义的消息类型，你需要在.proto上运行协议缓冲编译器protoc。如果你还没有安装编译器，请下载软件包，并按照 README 中的说明操作。对于Go，你还需要为编译器安装一个特殊的代码生成器插件：你可以在GitHub上的golang/protobuf仓库中找到这个插件和安装说明。

协议编译器的调用方法如下。
```Protobuf
protoc --proto_path=IMPORT_PATH --cpp_out=DST_DIR --java_out=DST_DIR --python_out=DST_DIR --go_out=DST_DIR --ruby_out=DST_DIR --objc_out=DST_DIR --csharp_out=DST_DIR path/to/file.proto
```
> IMPORT_PATH指定了一个目录，当解析导入指令时，可以在这个目录中查找.proto文件。如果省略，则使用当前目录。可以通过多次传递 --proto_path 选项来指定多个导入目录； 它们将按顺序被搜索。-I=_IMPORT_PATH_ 可以作为 --proto_path的简写。
你可以提供一个或多个输出指令。
> > --cpp_out会在 DST_DIR 中生成 C++ 代码。更多内容请参见C++生成代码参考。
> > --java_out在DST_DIR中生成Java代码。更多信息请参见Java生成的代码参考。
> > --python_out在DST_DIR中生成Python代码。更多信息请参考Python生成的代码。
> > --go_out 在 DST_DIR 中生成 Go 代码。更多信息请参见Go生成的代码参考。
> > --ruby_out 在 DST_DIR 中生成 Ruby 代码。Ruby生成的代码参考即将发布
> > --objc_out 在 DST_DIR 中生成 Objective-C 代码。更多内容请参考Objective-C生成的代码参考。
> > --csharp_out 在 DST_DIR 中生成 C# 代码。更多信息请参见C#生成的代码参考。
> > --php_out 在 DST_DIR 中生成 PHP 代码。作为额外的方便，如果DST_DIR以.zip或.jar结尾，编译器将把输出写到一个给定名称的ZIP格式的档案文件中。.jar输出也将被赋予一个Java JAR规范所要求的manifest文件。请注意，如果输出存档已经存在，它将被覆盖；编译器没有足够的智能来将文件添加到现有的存档中。
> 您必须提供一个或多个.proto文件作为输入。可以同时指定多个.proto文件。虽然文件是相对于当前目录命名的，但每个文件必须驻留在 IMPORT_PATHs 中，这样编译器才能确定它的规范名称。

[2]:	https://github.com/protocolbuffers/protobuf/blob/master/docs/third_party.md