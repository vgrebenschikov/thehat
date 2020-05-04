import React from "react";
import {
  Avatar, Box,
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

const NameCell = styled(Box)({
  display: 'flex',
  alignItems: 'center',
}) as typeof Box;

const PlayerAvatar = styled(Avatar)({
  marginRight: '12px',
}) as typeof Avatar;

const RotatedHeader = styled(Box)({
  width: '16px',
  marginTop: '48px',
  transform: 'rotate(-90deg)',
}) as typeof Box;

@inject('datastore')
@observer
class Results extends React.Component<{datastore?: DataStore}, {}> {
  render() {
    const {game} = this.props.datastore!;
    const {results} = game!;
    const users = Object.getOwnPropertyNames(results?.score)
                  .sort((u1, u2) => (results!.score[u2].total - results!.score[u1].total));
    return <>
      <ResultsTable component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Игрок</TableCell>
<<<<<<< HEAD
              <TableCell><RotatedHeader>Угадал</RotatedHeader></TableCell>
              <TableCell><RotatedHeader>Рассказал</RotatedHeader></TableCell>
=======
              <TableCell>Угадал</TableCell>
              <TableCell>Объяснил</TableCell>
>>>>>>> 637b3a7... Minor change of wording on results page
              <TableCell>Всего</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((u:any) => {
              const v = results?.score[u]!;
              return <TableRow key={u}>
                <TableCell><NameCell>
                  <PlayerAvatar src={game!.players[u]?.avatar}/>
                  {u}
                </NameCell></TableCell>
                <TableCell>{v.guessed}</TableCell>
                <TableCell>{v.explained}</TableCell>
                <TableCell>{v.total}</TableCell>
              </TableRow>
            })}
          </TableBody>
        </Table>
      </ResultsTable>
      <Card>
        <Button className="full-width-button" onClick={() => game!.sendRestart()}>Новая игра</Button>
      </Card>
    </>
  }
}
export default Results;