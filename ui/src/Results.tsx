import React from "react";
import {
  Button,
  Paper,
  styled,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from "@material-ui/core";
import {inject, observer} from "mobx-react";
import DataStore from "./store/DataStore";
import {Card} from "./common/Card";

const ResultsTable = styled(TableContainer)({
  marginBottom: '16px',
}) as typeof TableContainer;

@inject('datastore')
@observer
class Results extends React.Component<{datastore?: DataStore}, {}> {
  render() {
    const {game} = this.props.datastore!;
    const {results} = game!;
    const users = Object.getOwnPropertyNames(results?.score).sort();
    return <>
      <ResultsTable component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Игрок</TableCell>
              <TableCell>Угадал</TableCell>
              <TableCell>Рассказал</TableCell>
              <TableCell>Всего</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((u:any) => {
              const v = results?.score[u]!;
              return <TableRow key={u}>
                <TableCell>{u}</TableCell>
                <TableCell>{v.guessed}</TableCell>
                <TableCell>{v.explained}</TableCell>
                <TableCell>{v.total}</TableCell>
              </TableRow>
            })}
          </TableBody>
        </Table>
      </ResultsTable>
      <Card>
        <Button className="full-width-button" onClick={() => game!.sendReset()}>Новая игра</Button>
      </Card>
    </>
  }
}
export default Results;