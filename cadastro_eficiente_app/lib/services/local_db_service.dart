import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

class LocalDbService {
  static Database? _db;

  static Future<Database> get database async {
    if (_db != null) return _db!;
    _db = await _initDb();
    return _db!;
  }

  static Future<Database> _initDb() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'cadastro_eficiente.db');

    return await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE IF NOT EXISTS cadastros (
            id_ponto TEXT,
            username TEXT,
            nome_cadastrador TEXT,
            data_cadastro TEXT,
            hora_cadastro TEXT,
            latitude TEXT,
            longitude TEXT,
            tipo_coordenada TEXT,
            status_sincronizacao TEXT,
            dados_extras TEXT,
            fotos_json TEXT
          )
        ''');
      },
    );
  }

  static Future<void> salvarCadastro(Map<String, dynamic> cadastro) async {
    final db = await database;
    await db.insert('cadastros', cadastro);
  }

  static Future<List<Map<String, dynamic>>> listarCadastrosPendentes() async {
    final db = await database;

    final resultado = await db.rawQuery('''
      SELECT rowid as local_id, *
      FROM cadastros
      WHERE status_sincronizacao = ?
      ORDER BY rowid ASC
    ''', ['pendente']);

    return resultado;
  }

  static Future<void> marcarComoSincronizado(dynamic localId) async {
    final db = await database;

    await db.rawUpdate('''
      UPDATE cadastros
      SET status_sincronizacao = ?
      WHERE rowid = ?
    ''', ['sincronizado', localId]);
  }

  static Future<int> contarPendentes() async {
    final db = await database;

    final resultado = await db.rawQuery('''
      SELECT COUNT(*) as total
      FROM cadastros
      WHERE status_sincronizacao = ?
    ''', ['pendente']);

    return Sqflite.firstIntValue(resultado) ?? 0;
  }
}