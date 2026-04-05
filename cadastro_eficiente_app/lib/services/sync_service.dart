import 'dart:convert';
import 'package:sqflite/sqflite.dart';
import 'api_service.dart';

class SyncService {
  final Database db;
  final ApiService apiService;

  SyncService({
    required this.db,
    required this.apiService,
  });

  Future<void> sincronizarPendentes() async {
    final pendentes = await db.query(
      'cadastros',
      where: 'status_sync = ?',
      whereArgs: ['pendente'],
    );

    for (final cadastro in pendentes) {
      try {
        final cadastroIdLocal = cadastro['id_local'];

        final fotos = await db.query(
          'fotos',
          where: 'cadastro_id_local = ?',
          whereArgs: [cadastroIdLocal],
        );

        final caminhosFotos = fotos
            .map((f) => (f['caminho_arquivo'] ?? '').toString())
            .where((c) => c.isNotEmpty)
            .toList();

        await apiService.enviarCadastro(
          idPonto: (cadastro['id_ponto'] ?? '').toString(),
          nomeCadastrador: (cadastro['nome_cadastrador'] ?? '').toString(),
          dataCadastro: (cadastro['data_cadastro'] ?? '').toString(),
          horaCadastro: (cadastro['hora_cadastro'] ?? '').toString(),
          latitude: (cadastro['latitude'] ?? '').toString(),
          longitude: (cadastro['longitude'] ?? '').toString(),
          dadosExtrasJson: (cadastro['dados_extras_json'] ?? '{}').toString(),
          fotos: caminhosFotos,
        );

        await db.update(
          'cadastros',
          {'status_sync': 'sincronizado'},
          where: 'id_local = ?',
          whereArgs: [cadastroIdLocal],
        );

        await db.update(
          'fotos',
          {'status_sync': 'sincronizado'},
          where: 'cadastro_id_local = ?',
          whereArgs: [cadastroIdLocal],
        );
      } catch (e) {
        await db.update(
          'cadastros',
          {'status_sync': 'erro'},
          where: 'id_local = ?',
          whereArgs: [cadastro['id_local']],
        );
      }
    }
  }
}