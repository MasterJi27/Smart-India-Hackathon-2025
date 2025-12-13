class Note {
  final String id;
  final String subject;
  final String topic;
  final String content;
  final DateTime createdAt;

  Note({
    required this.id,
    required this.subject,
    required this.topic,
    required this.content,
    required this.createdAt,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'subject': subject,
        'topic': topic,
        'content': content,
        'createdAt': createdAt.toIso8601String(),
      };

  factory Note.fromJson(Map<String, dynamic> json) => Note(
        id: json['id'] as String,
        subject: json['subject'] as String,
        topic: json['topic'] as String,
        content: json['content'] as String,
        createdAt: DateTime.parse(json['createdAt'] as String),
      );
}
